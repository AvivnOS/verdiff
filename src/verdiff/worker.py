"""Isolated worker process for AST/inspect API extraction and sandboxed callable execution."""

from __future__ import annotations

import ast
import contextlib
import copy
import hashlib
import importlib
import importlib.metadata
import inspect
import io
import json
import pkgutil
import os
import random
import socket
import statistics
import sys
import time
import warnings
from pathlib import Path
from typing import Any

_SELF_SRC = str(Path(__file__).resolve().parents[1])
if _SELF_SRC not in sys.path:
    sys.path.append(_SELF_SRC)

from verdiff.codec import (  # noqa: E402
    decode_value,
    encode_value,
    strip_memory_addresses,
)

IPC_SENTINEL = "__VERDIFF_IPC__:"

_SKIP_MODULE_PARTS = {
    "test",
    "tests",
    "testing",
    "conftest",
    "benchmarks",
    "benchmark",
    "examples",
    "example",
    "docs",
    "scripts",
    "_vendor",
    "vendored",
    "contrib",
}

_DANGEROUS_CALLABLE_NAMES = {
    "exit",
    "quit",
    "kill",
    "system",
    "popen",
    "rmtree",
    "remove",
    "unlink",
    "sleep",
    "fork",
    "spawn",
    "spawnl",
    "spawnle",
    "spawnv",
    "spawnve",
    "execl",
    "execle",
    "execlp",
    "execv",
    "execve",
    "execvp",
    "abort",
    "_exit",
    "breakpoint",
    "input",
    "help",
    "license",
    "credits",
    "copyright",
}


def _disable_network() -> None:
    def _blocked(*_a: Any, **_kw: Any) -> Any:
        raise RuntimeError("VerDiff sandbox: outbound network disabled")

    socket.socket.connect = _blocked  # type: ignore[method-assign]
    socket.create_connection = _blocked  # type: ignore[assignment]


class _ASTFunctionInfo:
    def __init__(self) -> None:
        self.constants: list[Any] = []
        self.raised_exceptions: list[str] = []
        self.fingerprint: str = ""
        self.return_annotation: str | None = None


def _extract_ast_info_from_source(source: str) -> dict[str, _ASTFunctionInfo]:
    result: dict[str, _ASTFunctionInfo] = {}
    try:
        tree = ast.parse(source)
    except Exception:
        return result

    def _visit_scope(body: list[ast.stmt], prefix: str) -> None:
        for node in body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                qual = f"{prefix}.{node.name}" if prefix else node.name
                result[qual] = _analyze_func_node(node)
            elif isinstance(node, ast.ClassDef):
                cls_qual = f"{prefix}.{node.name}" if prefix else node.name
                _visit_scope(node.body, cls_qual)

    _visit_scope(tree.body, "")
    return result


def _analyze_func_node(node: ast.FunctionDef | ast.AsyncFunctionDef) -> _ASTFunctionInfo:
    info = _ASTFunctionInfo()
    if node.returns is not None:
        try:
            info.return_annotation = ast.unparse(node.returns)
        except Exception:
            pass

    stmts = list(node.body)
    if (
        stmts
        and isinstance(stmts[0], ast.Expr)
        and isinstance(stmts[0].value, ast.Constant)
        and isinstance(stmts[0].value.value, str)
    ):
        stmts = stmts[1:]

    constants_seen: set[tuple[type, Any]] = set()
    raised_seen: set[str] = set()

    for stmt in stmts:
        for child in ast.walk(stmt):
            if isinstance(child, ast.Constant):
                val = child.value
                if isinstance(val, (str, int, float, bytes)) and not isinstance(val, bool):
                    if isinstance(val, (str, bytes)) and len(val) > 120:
                        continue
                    key = (type(val), val)
                    if key not in constants_seen and len(info.constants) < 28:
                        constants_seen.add(key)
                        info.constants.append(val)
            elif isinstance(child, ast.Raise) and child.exc is not None:
                exc_name = None
                if isinstance(child.exc, ast.Call):
                    if isinstance(child.exc.func, ast.Name):
                        exc_name = child.exc.func.id
                    elif isinstance(child.exc.func, ast.Attribute):
                        exc_name = child.exc.func.attr
                elif isinstance(child.exc, ast.Name):
                    exc_name = child.exc.id
                if exc_name and exc_name not in raised_seen:
                    raised_seen.add(exc_name)
                    info.raised_exceptions.append(exc_name)

    try:
        mod_wrapper = ast.Module(body=stmts, type_ignores=[])
        dumped = ast.dump(mod_wrapper, annotate_fields=True, include_attributes=False)
        info.fingerprint = hashlib.sha256(dumped.encode("utf-8")).hexdigest()[:16]
    except Exception:
        info.fingerprint = ""

    return info


def _resolve_root_import_names(package_name: str) -> list[str]:
    candidates: list[str] = []
    try:
        dist = importlib.metadata.distribution(package_name)
        top_level = dist.read_text("top_level.txt")
        if top_level:
            for line in top_level.splitlines():
                clean = line.strip().split("/")[0].split("\\")[0]
                if clean and not clean.startswith("_") and clean not in candidates:
                    candidates.append(clean)
        if not candidates and dist.files:
            for f in dist.files:
                parts = f.parts
                if len(parts) >= 2 and parts[0].endswith(".dist-info"):
                    continue
                if parts and not parts[0].startswith("_") and not parts[0].endswith(".dist-info"):
                    mod_name = parts[0][:-3] if parts[0].endswith(".py") else parts[0]
                    if mod_name.isidentifier() and mod_name not in candidates:
                        candidates.append(mod_name)
    except Exception:
        pass

    normalized = package_name.replace("-", "_").strip()
    if normalized and normalized not in candidates:
        candidates.append(normalized)
    return candidates


def _discover_public_modules(package_name: str, explicit_modules: list[str] | None = None) -> list[str]:
    if explicit_modules:
        return explicit_modules

    roots = _resolve_root_import_names(package_name)
    discovered: list[str] = []
    for root_name in roots:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                root_mod = importlib.import_module(root_name)
        except Exception:
            continue

        if root_name not in discovered:
            discovered.append(root_name)

        pkg_path = getattr(root_mod, "__path__", None)
        if pkg_path:
            try:
                for mod_info in pkgutil.walk_packages(pkg_path, prefix=f"{root_name}."):
                    parts = mod_info.name.split(".")
                    if any(p.startswith("_") or p.lower() in _SKIP_MODULE_PARTS for p in parts):
                        continue
                    if mod_info.name not in discovered:
                        discovered.append(mod_info.name)
                    if len(discovered) >= 120:
                        break
            except Exception:
                pass
    return discovered


def _extract_parameters(sig: inspect.Signature, skip_first: bool = False) -> list[dict[str, Any]]:
    params_out: list[dict[str, Any]] = []
    params_list = list(sig.parameters.values())
    if skip_first and params_list:
        params_list = params_list[1:]

    for p in params_list:
        ann_str: str | None = None
        if p.annotation is not inspect.Parameter.empty:
            if isinstance(p.annotation, str):
                ann_str = p.annotation
            elif hasattr(p.annotation, "__name__") and getattr(p.annotation, "__module__", "builtins") == "builtins":
                ann_str = p.annotation.__name__
            else:
                ann_str = strip_memory_addresses(str(p.annotation)).replace("typing.", "")

        has_def = p.default is not inspect.Parameter.empty
        def_repr = strip_memory_addresses(repr(p.default)) if has_def else None
        def_tagged = encode_value(p.default) if has_def else None

        params_out.append(
            {
                "name": p.name,
                "kind": str(p.kind.name),
                "annotation": ann_str,
                "has_default": has_def,
                "default_repr": def_repr,
                "default_value_tagged": def_tagged,
            }
        )
    return params_out


def _return_annotation_str(sig: inspect.Signature, ast_ret: str | None) -> str | None:
    if sig.return_annotation is not inspect.Signature.empty:
        if isinstance(sig.return_annotation, str):
            return sig.return_annotation
        if hasattr(sig.return_annotation, "__name__") and getattr(sig.return_annotation, "__module__", "builtins") == "builtins":
            return sig.return_annotation.__name__
        return strip_memory_addresses(str(sig.return_annotation)).replace("typing.", "")
    return ast_ret


def extract_api_surface(package_name: str, explicit_modules: list[str] | None = None) -> dict[str, Any]:
    """Extract all public functions, classes, methods, and stateful object call chains."""
    modules = _discover_public_modules(package_name, explicit_modules)
    root_prefixes = tuple(_resolve_root_import_names(package_name))
    contracts: list[dict[str, Any]] = []
    seen_targets: set[tuple[str, str]] = set()
    seen_private_reexports: set[tuple[str, str]] = set()

    for mod_name in modules:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                mod = importlib.import_module(mod_name)
        except Exception:
            continue

        ast_map: dict[str, _ASTFunctionInfo] = {}
        try:
            src_file = inspect.getsourcefile(mod)
            if src_file and Path(src_file).is_file():
                source_code = Path(src_file).read_text(encoding="utf-8", errors="replace")
                ast_map = _extract_ast_info_from_source(source_code)
        except Exception:
            pass

        explicit_all = getattr(mod, "__all__", None)
        if isinstance(explicit_all, (list, tuple, set)):
            member_names = [n for n in explicit_all if isinstance(n, str) and not n.startswith("_")]
            for attr_name in dir(mod):
                if not attr_name.startswith("_") and attr_name not in member_names:
                    try:
                        attr_obj = getattr(mod, attr_name)
                        if getattr(attr_obj, "__module__", None) == mod_name:
                            member_names.append(attr_name)
                    except Exception:
                        pass
        else:
            member_names = [n for n in dir(mod) if not n.startswith("_")]

        for name in sorted(set(member_names)):
            if name in _DANGEROUS_CALLABLE_NAMES:
                continue
            try:
                obj = getattr(mod, name)
            except Exception:
                continue

            obj_mod = getattr(obj, "__module__", "") or ""
            if obj_mod and not obj_mod.startswith(root_prefixes):
                if not (isinstance(explicit_all, (list, tuple, set)) and name in explicit_all):
                    continue
            canonical_mod = obj_mod if (obj_mod and obj_mod in modules) else mod_name
            if obj_mod and obj_mod not in modules:
                # Re-exported from a private module (e.g. urllib3._collections.HTTPHeaderDict):
                # deduplicate across submodules so we don't fuzz identical re-exports 3 times.
                if mod_name in root_prefixes and len(modules) > 1:
                    # Prefer the concrete submodule (e.g. urllib3.connection) if root only re-exported it in one version
                    pass
                priv_key = (obj_mod, name)
                if priv_key in seen_private_reexports:
                    continue
                if mod_name not in root_prefixes or len(modules) == 1:
                    seen_private_reexports.add(priv_key)
                else:
                    continue

            if inspect.isfunction(obj) or inspect.isbuiltin(obj):
                target_key = (canonical_mod, name)
                if target_key in seen_targets:
                    continue
                try:
                    sig = inspect.signature(obj)
                except (ValueError, TypeError):
                    continue
                seen_targets.add(target_key)
                ast_info = ast_map.get(name, _ASTFunctionInfo())
                doc = inspect.getdoc(obj)
                contracts.append(
                    {
                        "qualname": name,
                        "module": canonical_mod,
                        "callable_kind": "function",
                        "parameters": _extract_parameters(sig, skip_first=False),
                        "return_annotation": _return_annotation_str(sig, ast_info.return_annotation),
                        "docstring_summary": doc.splitlines()[0][:160] if doc else None,
                        "ast_constants": [encode_value(c) for c in ast_info.constants],
                        "raised_exceptions": ast_info.raised_exceptions,
                        "body_ast_fingerprint": ast_info.fingerprint,
                        "class_init_params": [],
                        "chain_methods": [],
                    }
                )

            elif inspect.isclass(obj):
                if issubclass(obj, BaseException):
                    continue
                target_key = (canonical_mod, name)
                if target_key in seen_targets:
                    continue
                seen_targets.add(target_key)

                init_params: list[dict[str, Any]] = []
                init_ast = ast_map.get(f"{name}.__init__", _ASTFunctionInfo())
                instantiable = False
                try:
                    sig = inspect.signature(obj)
                    init_params = _extract_parameters(sig, skip_first=False)
                    instantiable = True
                    doc = inspect.getdoc(obj)
                    contracts.append(
                        {
                            "qualname": name,
                            "module": canonical_mod,
                            "callable_kind": "class",
                            "parameters": init_params,
                            "return_annotation": name,
                            "docstring_summary": doc.splitlines()[0][:160] if doc else None,
                            "ast_constants": [encode_value(c) for c in init_ast.constants],
                            "raised_exceptions": init_ast.raised_exceptions,
                            "body_ast_fingerprint": init_ast.fingerprint,
                            "class_init_params": [],
                            "chain_methods": [],
                        }
                    )
                except (ValueError, TypeError):
                    pass

                regular_methods_for_chain: list[dict[str, Any]] = []
                class_consts: list[Any] = list(init_ast.constants)

                for attr_name, raw_attr in inspect.getmembers(obj):
                    if attr_name.startswith("_") or attr_name in _DANGEROUS_CALLABLE_NAMES:
                        continue
                    qual = f"{name}.{attr_name}"
                    if (canonical_mod, qual) in seen_targets:
                        continue

                    static_raw = inspect.getattr_static(obj, attr_name, None)
                    method_kind: str | None = None
                    skip_self = False
                    if isinstance(static_raw, staticmethod):
                        method_kind = "staticmethod"
                        skip_self = False
                    elif isinstance(static_raw, classmethod):
                        method_kind = "classmethod"
                        skip_self = True
                    elif inspect.isfunction(raw_attr) or inspect.ismethod(raw_attr):
                        defining_mod = getattr(raw_attr, "__module__", "") or ""
                        if defining_mod == "builtins":
                            continue
                        method_kind = "method"
                        skip_self = True

                    if method_kind is None:
                        continue

                    try:
                        msig = inspect.signature(raw_attr)
                    except (ValueError, TypeError):
                        continue

                    seen_targets.add((canonical_mod, qual))
                    m_ast = ast_map.get(qual, _ASTFunctionInfo())
                    mdoc = inspect.getdoc(raw_attr)
                    extracted_m_params = _extract_parameters(
                        msig,
                        skip_first=(skip_self and method_kind == "method" and "self" in msig.parameters),
                    )
                    for c_val in m_ast.constants:
                        if c_val not in class_consts and len(class_consts) < 32:
                            class_consts.append(c_val)

                    contracts.append(
                        {
                            "qualname": qual,
                            "module": canonical_mod,
                            "callable_kind": method_kind,
                            "parameters": extracted_m_params,
                            "return_annotation": _return_annotation_str(msig, m_ast.return_annotation),
                            "docstring_summary": mdoc.splitlines()[0][:160] if mdoc else None,
                            "ast_constants": [encode_value(c) for c in (m_ast.constants + init_ast.constants)[:24]],
                            "raised_exceptions": m_ast.raised_exceptions,
                            "body_ast_fingerprint": m_ast.fingerprint,
                            "class_init_params": init_params if method_kind == "method" else [],
                            "chain_methods": [],
                        }
                    )

                    if method_kind == "method":
                        regular_methods_for_chain.append(
                            {
                                "name": attr_name,
                                "parameters": extracted_m_params,
                            }
                        )

                if instantiable and len(regular_methods_for_chain) >= 2:
                    chain_qual = f"{name}.<stateful_chain>"
                    seen_targets.add((canonical_mod, chain_qual))
                    contracts.append(
                        {
                            "qualname": chain_qual,
                            "module": canonical_mod,
                            "callable_kind": "stateful_chain",
                            "parameters": init_params,
                            "return_annotation": name,
                            "docstring_summary": f"Multi-step stateful method call chain on {name}",
                            "ast_constants": [encode_value(c) for c in class_consts[:28]],
                            "raised_exceptions": [],
                            "body_ast_fingerprint": init_ast.fingerprint,
                            "class_init_params": init_params,
                            "chain_methods": regular_methods_for_chain[:10],
                        }
                    )

    return {"contracts": contracts, "modules_scanned": modules}


def _resolve_callable(module_name: str, qualname: str) -> tuple[Any, Any]:
    mod = importlib.import_module(module_name)
    if qualname.endswith(".<stateful_chain>"):
        cls_name = qualname[: -len(".<stateful_chain>")]
        cls = getattr(mod, cls_name)
        return cls, cls
    parts = qualname.split(".")
    if len(parts) == 1:
        return None, getattr(mod, parts[0])
    cls = getattr(mod, parts[0])
    return cls, getattr(cls, parts[1])


def _extract_instance_mutation_delta(
    inst_before: dict[str, Any] | None,
    inst_after: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Return ONLY the attributes/representations of `instance` that actually mutated during the call."""
    if inst_before is None or inst_after is None or inst_before == inst_after:
        return None
    if inst_before.get("__t__") != "object" or inst_after.get("__t__") != "object":
        return inst_after

    st_before = inst_before.get("state", {})
    st_after = inst_after.get("state", {})
    delta_state: dict[str, Any] = {}
    if isinstance(st_before, dict) and isinstance(st_after, dict):
        for k, v_after in st_after.items():
            if k not in st_before or st_before[k] != v_after:
                delta_state[k] = v_after
        for k in st_before:
            if k not in st_after:
                delta_state[k] = {"__t__": "removed_attr"}

    str_changed = inst_after.get("str") != inst_before.get("str")
    repr_changed = inst_after.get("repr") != inst_before.get("repr")
    if not delta_state and not str_changed and not repr_changed:
        return None

    return {
        "__t__": "object",
        "cls": inst_after.get("cls"),
        "str": inst_after.get("str", "") if str_changed else "",
        "repr": inst_after.get("repr", "") if repr_changed else "",
        "state": delta_state,
    }


def _invoke_once(
    module_name: str,
    qualname: str,
    callable_kind: str,
    tagged_args: list[Any],
    tagged_kwargs: dict[str, Any],
    tagged_inst_args: list[Any],
    tagged_inst_kwargs: dict[str, Any],
    tagged_method_chain: list[Any] | None = None,
) -> dict[str, Any]:
    args = [decode_value(a) for a in tagged_args]
    kwargs = {k: decode_value(v) for k, v in tagged_kwargs.items()}
    inst_args = [decode_value(a) for a in tagged_inst_args]
    inst_kwargs = {k: decode_value(v) for k, v in tagged_inst_kwargs.items()}
    method_chain: list[tuple[str, list[Any], dict[str, Any]]] = []
    for step in tagged_method_chain or []:
        m_name = str(step[0])
        m_args = [decode_value(a) for a in step[1]]
        m_kw = {k: decode_value(v) for k, v in step[2].items()}
        method_chain.append((m_name, m_args, m_kw))

    args_before = encode_value(args)
    kwargs_before = encode_value(kwargs)
    chain_args_before = encode_value([(m_a, m_k) for _, m_a, m_k in method_chain]) if method_chain else None

    cls_obj, target = _resolve_callable(module_name, qualname)

    out_buf = io.StringIO()
    err_buf = io.StringIO()
    instance = None
    inst_before = None

    with warnings.catch_warnings(), contextlib.redirect_stdout(out_buf), contextlib.redirect_stderr(err_buf):
        warnings.simplefilter("ignore")
        random.seed(42)
        _orig_urandom = os.urandom
        os.urandom = random.Random(42).randbytes
        t0 = time.perf_counter_ns()
        try:
            if callable_kind == "stateful_chain" and cls_obj is not None:
                instance = cls_obj(*copy.deepcopy(inst_args), **copy.deepcopy(inst_kwargs))
                inst_before = encode_value(instance)
                step_results = []
                for m_name, m_args, m_kw in method_chain:
                    bound_fn = getattr(instance, m_name)
                    r = bound_fn(*m_args, **m_kw)
                    if inspect.isgenerator(r) or type(r).__name__ in ("map", "filter", "zip", "enumerate", "reversed"):
                        r = [item for idx, item in enumerate(r) if idx < 64]
                    step_results.append(r)
                result = step_results
            elif callable_kind == "method" and cls_obj is not None:
                instance = cls_obj(*copy.deepcopy(inst_args), **copy.deepcopy(inst_kwargs))
                inst_before = encode_value(instance)
                bound_method = getattr(instance, qualname.split(".")[1])
                result = bound_method(*args, **kwargs)
            elif callable_kind == "classmethod" and cls_obj is not None:
                bound_cm = getattr(cls_obj, qualname.split(".")[1])
                result = bound_cm(*args, **kwargs)
            elif callable_kind == "staticmethod" and cls_obj is not None:
                bound_sm = getattr(cls_obj, qualname.split(".")[1])
                result = bound_sm(*args, **kwargs)
            else:
                result = target(*args, **kwargs)

            if inspect.isgenerator(result) or type(result).__name__ in ("map", "filter", "zip", "enumerate", "reversed"):
                materialized = []
                for idx, item in enumerate(result):
                    if idx >= 64:
                        break
                    materialized.append(item)
                result = materialized

            elapsed_ms = (time.perf_counter_ns() - t0) / 1_000_000.0
        except BaseException as exc:
            elapsed_ms = (time.perf_counter_ns() - t0) / 1_000_000.0
            exc_cls = type(exc)
            return {
                "status": "exception",
                "exception_type": exc_cls.__qualname__,
                "exception_module": exc_cls.__module__,
                "exception_message": strip_memory_addresses(str(exc))[:300],
                "duration_ms": elapsed_ms,
            }
        finally:
            os.urandom = _orig_urandom

    args_after = encode_value(args)
    kwargs_after = encode_value(kwargs)
    inst_after = encode_value(instance) if instance is not None else None
    chain_args_after = encode_value([(m_a, m_k) for _, m_a, m_k in method_chain]) if method_chain else None

    mutated_args = None
    if args_after != args_before:
        mutated_args = args_after
    elif chain_args_after != chain_args_before:
        mutated_args = chain_args_after

    mutated_inst_delta = _extract_instance_mutation_delta(inst_before, inst_after)

    res_cls = type(result)
    res_type_fqn = f"{res_cls.__module__}.{res_cls.__qualname__}"
    return {
        "status": "ok",
        "return_type": res_type_fqn,
        "return_repr": strip_memory_addresses(repr(result))[:300],
        "return_canonical": encode_value(result),
        "mutated_args_after": mutated_args,
        "mutated_kwargs_after": kwargs_after if kwargs_after != kwargs_before else None,
        "mutated_instance_after": mutated_inst_delta,
        "duration_ms": elapsed_ms,
    }


def _benchmark_callable(
    module_name: str,
    qualname: str,
    callable_kind: str,
    tagged_args: list[Any],
    tagged_kwargs: dict[str, Any],
    tagged_inst_args: list[Any],
    tagged_inst_kwargs: dict[str, Any],
    tagged_method_chain: list[Any] | None = None,
    repeats: int = 5,
) -> dict[str, Any]:
    first = _invoke_once(
        module_name,
        qualname,
        callable_kind,
        tagged_args,
        tagged_kwargs,
        tagged_inst_args,
        tagged_inst_kwargs,
        tagged_method_chain,
    )
    if first["status"] != "ok":
        return {"status": first["status"], "median_duration_ms": first.get("duration_ms", 0.0)}

    samples: list[float] = []
    for _ in range(max(3, repeats)):
        run_res = _invoke_once(
            module_name,
            qualname,
            callable_kind,
            tagged_args,
            tagged_kwargs,
            tagged_inst_args,
            tagged_inst_kwargs,
            tagged_method_chain,
        )
        samples.append(float(run_res.get("duration_ms", 0.0)))

    return {
        "status": "ok",
        "median_duration_ms": statistics.median(samples),
        "samples": samples,
    }


def main() -> None:
    proto_out = sys.stdout
    _disable_network()
    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception as exc:
            resp = {"ok": False, "error": f"Invalid JSON request: {exc}"}
            proto_out.write(f"\n{IPC_SENTINEL}{json.dumps(resp)}\n")
            proto_out.flush()
            continue

        cmd = req.get("cmd")
        try:
            if cmd == "ping":
                resp = {"ok": True, "python_version": sys.version.split()[0]}
            elif cmd == "extract":
                data = extract_api_surface(req["package"], req.get("modules"))
                resp = {"ok": True, "data": data}
            elif cmd == "execute":
                outcome = _invoke_once(
                    req["module"],
                    req["qualname"],
                    req.get("callable_kind", "function"),
                    req.get("args", []),
                    req.get("kwargs", {}),
                    req.get("instance_args", []),
                    req.get("instance_kwargs", {}),
                    req.get("method_chain", []),
                )
                resp = {"ok": True, "outcome": outcome}
            elif cmd == "benchmark":
                bench = _benchmark_callable(
                    req["module"],
                    req["qualname"],
                    req.get("callable_kind", "function"),
                    req.get("args", []),
                    req.get("kwargs", {}),
                    req.get("instance_args", []),
                    req.get("instance_kwargs", {}),
                    req.get("method_chain", []),
                    repeats=int(req.get("repeats", 5)),
                )
                resp = {"ok": True, "benchmark": bench}
            elif cmd == "quit":
                resp = {"ok": True, "bye": True}
                proto_out.write(f"\n{IPC_SENTINEL}{json.dumps(resp)}\n")
                proto_out.flush()
                break
            else:
                resp = {"ok": False, "error": f"Unknown command: {cmd}"}
        except BaseException as exc:
            resp = {
                "ok": False,
                "error": f"{type(exc).__name__}: {strip_memory_addresses(str(exc))[:300]}",
            }

        proto_out.write(f"\n{IPC_SENTINEL}{json.dumps(resp)}\n")
        proto_out.flush()


if __name__ == "__main__":
    main()
