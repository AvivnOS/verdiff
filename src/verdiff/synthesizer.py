"""Smart Edge-Case, Type-Guided, White-Box AST & Stateful Call-Chain Input Synthesizer."""

from __future__ import annotations

import datetime
import decimal
import hashlib
import pathlib
import random
import re
from typing import Any

from verdiff.codec import decode_value, encode_value
from verdiff.models import CallableContract, ParameterSpec, SynthesizedInput

_UNIVERSAL_STRINGS: list[str] = [
    "",
    " ",
    "\t\r\n",
    "a",
    "test",
    "0",
    "-1",
    "1.0.0",
    "שלום עולם \u202eRTL\u202c",
    " café_naïve_🔥 ",
    "null\x00byte",
    "<script>alert('x')&\"'</script>",
    "https://example.com:8080/a/b?q=1#top",
    "../../etc/passwd",
    "{0} %s ${var}",
    "'" + ("\\" * 26),
    "[" * 45 + "x" + "]" * 45,
]

_UNIVERSAL_INTS: list[int] = [
    0,
    1,
    -1,
    2,
    -2,
    10,
    255,
    256,
    4096,
    65535,
    65536,
    -65536,
]

_UNIVERSAL_FLOATS: list[float] = [
    0.0,
    -0.0,
    1.0,
    -1.0,
    0.5,
    1e-9,
    1e18,
    float("inf"),
    float("-inf"),
    float("nan"),
]

_UNIVERSAL_BYTES: list[bytes] = [
    b"",
    b"a",
    b"ascii_bytes",
    b"\x00\xff\xfe\xfd",
    "שלום".encode("utf-8"),
    b" \t\r\n",
]

_DOMAIN_POOLS: dict[str, list[Any]] = {
    "version": [
        "1.0.0",
        "1.0",
        "0.0.1",
        "2.1.0-alpha.1",
        "1.0.0+20130313",
        "1.0-dev",
        "1.0a1",
        "1.0.post1",
        "1!2.0.0",
        "v1.2.3",
        "1.0.0.0",
        "01.1.0",
        "invalid-version",
        "legacy_foo_bar",
        "",
        "1.0.0-0.3.7",
        "1.0.0+local_1",
    ],
    "spec": [
        "==1.0.0.*",
        ">=1.0.0",
        "==1.0.*",
        "~=1.4.2",
        "!=1.0",
        ">=1.0,<2.0",
        "===1.0-legacy",
        ">=1.0.*",
        "<=0.1a1",
        "invalid_spec",
        "",
    ],
    "requirement": [
        "pkg>=1.0.0",
        "pkg>=1.0.*",
        "pkg>=1.0+local",
        "pkg @ http:///path",
        "pkg @ https://example.com/pkg.whl",
        "pkg==1.0.*",
        "pkg[extra]>=1.0",
        "pkg~=1.4.2",
        "invalid_req",
        "",
    ],
    "marker": [
        'python_version >= "3.8"',
        'os_name == "a" b',
        'sys_platform == "win32" and python_version < "3.12"',
        'extra == "test_extra"',
        "invalid_marker",
        "",
    ],
    "tag_str": [
        "py3-none-any",
        "py 3",
        "cp312-cp312-manylinux_2_17_x86_64",
        "invalid_tag",
        "",
    ],
    "url": [
        "https://example.com/path?a=1&b=2#sec",
        "http://example.com:8080/test",
        "http://[::1]:8000/ipv6",
        "http://user:pass@example.com:80/auth",
        "http://example.com:99999/badport",
        "http://example.com/path with spaces",
        "javascript:alert(1)",
        "mailto:test@example.com",
        "//example.com/schemeless",
        "https://שלום.example.com/ראשי",
        "http:///emptyhost",
        "http://example.com:0/",
        "",
    ],
    "html": [
        "<p>Hello <b>World</b></p>",
        "<script>alert('xss')&\"'</script>",
        '<a href="javascript:alert(1)">click</a>',
        '<a href="http://example.com" title="ok">valid</a>',
        '<a href="custom://proto">custom</a>',
        '<img src="x" onerror="alert(1)">',
        "<!-- comment --><div class='x'>שלום</div>",
        "plain & simple < > \" '",
        "",
    ],
    "sql": [
        "'" + ("\\" * 26),
        "SELECT a, b FROM users WHERE id = 1;",
        "SELECT 1 WHERE a IN (1);",
        "WITH a AS (SELECT 1), b AS (SELECT 2) SELECT * FROM b;",
        "--hello\r\nSELECT 1;--world\nSELECT 2;",
        "INSERT INTO tbl VALUES (1, 'a');",
        "",
    ],
    "path": [
        "sandbox_sample.txt",
        "sub/nested.json",
        "./a/../b/file.py",
        pathlib.Path("sandbox_sample.txt"),
        "",
    ],
    "pattern": [
        r"^[a-zA-Z0-9_]+$",
        r"(\d+)-(\w+)",
        r".*",
        re.compile(r"^[a-z]+$"),
        "",
    ],
    "mapping": [
        {},
        {"a": "1", "b": "2"},
        {"a": 1, "b": "two"},
        {"": None, "nested": {"x": [1, 2]}},
        {"Accept": "application/json", "Content-Type": "text/plain; charset=utf-8"},
    ],
    "sequence": [
        [],
        ["1.0.0", "1.0", "2.0.0"],
        ["a", "b", "c"],
        [1, 2, 3],
        [3, 1, 2, 1],
        ["http", "https", "mailto"],
        [None, ""],
        (1, 2),
    ],
}


def _infer_domain_from_param_name(name: str) -> str | None:
    low = name.lower()
    if any(k in low for k in ("requirement", "req_str", "req")):
        return "requirement"
    if "marker" in low:
        return "marker"
    if any(k in low for k in ("spec", "constraint", "match_expr")):
        return "spec"
    if any(k in low for k in ("version", "ver", "prerelease", "epoch", "release", "prospective")):
        return "version"
    if any(k in low for k in ("interpreter", "abi", "platform", "tag")):
        return "tag_str"
    if any(k in low for k in ("url", "uri", "href", "endpoint", "origin", "host")):
        return "url"
    if any(k in low for k in ("sql", "stmt", "statement", "query")):
        return "sql"
    if any(k in low for k in ("html", "markup", "xml", "fragment", "text")):
        return "html"
    if any(k in low for k in ("path", "file", "filename", "dirname")):
        return "path"
    if any(k in low for k in ("pattern", "regex", "regexp")):
        return "pattern"
    if any(k in low for k in ("dict", "map", "mapping", "headers", "params", "attrs", "attributes", "options", "config", "data", "env")):
        return "mapping"
    if any(k in low for k in ("list", "seq", "items", "elements", "iterable", "tags", "protocols", "methods", "values", "keys", "args")):
        return "sequence"
    return None


def _candidates_for_annotation(
    ann: str | None,
    param_name: str,
    default_val: Any,
    has_default: bool,
    ast_consts: list[Any],
    rng: random.Random,
) -> list[Any]:
    pool: list[Any] = []

    if has_default:
        pool.append(default_val)
        if isinstance(default_val, bool):
            pool.append(not default_val)
        elif isinstance(default_val, int):
            pool.extend([default_val + 1, default_val - 1, 0, -1])
        elif isinstance(default_val, str) and default_val:
            pool.extend(["", default_val.upper(), default_val + "_invalid"])

    domain = _infer_domain_from_param_name(param_name)
    if domain and domain in _DOMAIN_POOLS:
        pool.extend(_DOMAIN_POOLS[domain])

    ann_low = (ann or "").lower().strip()

    for c in ast_consts:
        if isinstance(c, str):
            pool.append(c)
            if len(c) < 40:
                pool.append(c + "_diff")
        elif isinstance(c, int) and not isinstance(c, bool):
            pool.extend([c, c + 1, c - 1])
        elif isinstance(c, float):
            pool.extend([c, c + 0.5, -c])
        elif isinstance(c, bytes):
            pool.append(c)

    if not ann_low or "any" in ann_low or "object" in ann_low:
        pool.extend(_UNIVERSAL_STRINGS)
        pool.extend([b"a", b"bytes", None, 0, 1, -1, True, False, 1.5, float("nan"), [], ["1.0.0"], [1, 2], {"a": 1}])
    else:
        if "optional" in ann_low or "none" in ann_low:
            pool.append(None)
        if "bool" in ann_low:
            pool.extend([True, False, 0, 1, None])
        if "int" in ann_low:
            pool.extend(_UNIVERSAL_INTS)
        if "float" in ann_low or "number" in ann_low:
            pool.extend(_UNIVERSAL_FLOATS)
            pool.extend([0, 1, -1])
        if "decimal" in ann_low:
            pool.extend(
                [
                    decimal.Decimal("0"),
                    decimal.Decimal("-0.0"),
                    decimal.Decimal("123.456"),
                    decimal.Decimal("-999999999.99"),
                    decimal.Decimal("Infinity"),
                    decimal.Decimal("NaN"),
                ]
            )
        if "str" in ann_low or "markup" in ann_low or "literal" in ann_low:
            pool.extend(_UNIVERSAL_STRINGS)
            pool.append(b"a")
        if "bytes" in ann_low or "buffer" in ann_low:
            pool.extend(_UNIVERSAL_BYTES)
            pool.append(bytearray(b"mutable_bytes"))
        if "datetime" in ann_low:
            pool.extend(
                [
                    datetime.datetime(2026, 1, 1, 0, 0, 0),
                    datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc),
                    datetime.datetime(2000, 2, 29, 23, 59, 59),
                ]
            )
        elif "date" in ann_low:
            pool.extend(
                [
                    datetime.date(2026, 1, 1),
                    datetime.date(1970, 1, 1),
                    datetime.date(2000, 2, 29),
                ]
            )
        if "path" in ann_low:
            pool.extend(_DOMAIN_POOLS["path"])
        if "pattern" in ann_low or "regex" in ann_low:
            pool.extend(_DOMAIN_POOLS["pattern"])
        if any(k in ann_low for k in ("list", "sequence", "iterable", "collection", "set", "tuple")):
            pool.extend(
                [
                    [],
                    ["1.0.0", "1.0"],
                    [1, 2, 3],
                    [3, 1, 2],
                    ["a", "b"],
                    [""],
                    [None],
                    (1, 2),
                    {"a", "b"},
                ]
            )
        if any(k in ann_low for k in ("dict", "mapping")):
            pool.extend(_DOMAIN_POOLS["mapping"])

    pool.extend([None, "", 0, -1, [], {}])

    deduped: list[Any] = []
    seen_hashes: set[str] = set()
    for item in pool:
        h = _canonical_hash(item)
        if h not in seen_hashes:
            seen_hashes.add(h)
            deduped.append(item)

    if len(deduped) > 16:
        head = deduped[:14]
        tail = deduped[14:]
        rng.shuffle(tail)
        deduped = head + tail

    return deduped


def _canonical_hash(val: Any) -> str:
    encoded = repr(encode_value(val))
    return hashlib.sha1(encoded.encode("utf-8")).hexdigest()[:16]


class InputSynthesizer:
    """Synthesizes deterministic, deduplicated test vectors and stateful call chains for callable pairs."""

    def __init__(self, seed: int = 42, max_inputs_per_callable: int = 80) -> None:
        self.seed = seed
        self.max_inputs_per_callable = max_inputs_per_callable

    def synthesize_for_pair(
        self,
        contract_v1: CallableContract,
        contract_v2: CallableContract,
    ) -> list[SynthesizedInput]:
        rng = random.Random(f"{self.seed}:{contract_v1.full_id}")

        ast_consts: list[Any] = []
        for raw_c in contract_v1.ast_constants + contract_v2.ast_constants:
            ast_consts.append(decode_value(raw_c))

        if contract_v1.callable_kind == "stateful_chain":
            return self._synthesize_stateful_chains(contract_v1, contract_v2, ast_consts, rng)

        inst_variants: list[tuple[list[Any], dict[str, Any]]] = [([], {})]
        if contract_v1.callable_kind == "method" and contract_v1.class_init_params:
            inst_variants = self._build_instance_variants(
                contract_v1.class_init_params, ast_consts, rng
            )
        inst_args_default, inst_kwargs_default = inst_variants[0]

        params = contract_v1.parameters
        pos_params = [
            p for p in params if p.kind in ("POSITIONAL_ONLY", "POSITIONAL_OR_KEYWORD")
        ]
        kw_only_params = [p for p in params if p.kind == "KEYWORD_ONLY"]
        has_var_pos = any(p.kind == "VAR_POSITIONAL" for p in params)

        param_pools: dict[str, list[Any]] = {}
        for p in pos_params + kw_only_params:
            def_val = decode_value(p.default_value_tagged) if p.has_default else None
            param_pools[p.name] = _candidates_for_annotation(
                p.annotation,
                p.name,
                def_val,
                p.has_default,
                ast_consts,
                rng,
            )

        inputs: list[SynthesizedInput] = []
        seen_vectors: set[str] = set()

        def _add_vector(
            args: list[Any],
            kwargs: dict[str, Any],
            strategy: str,
            desc: str = "",
            inst_override: tuple[list[Any], dict[str, Any]] | None = None,
        ) -> None:
            if len(inputs) >= self.max_inputs_per_callable:
                return
            ia, ik = inst_override if inst_override is not None else (inst_args_default, inst_kwargs_default)
            vec_hash = _canonical_hash((args, kwargs, ia, ik))
            if vec_hash in seen_vectors:
                return
            seen_vectors.add(vec_hash)
            inputs.append(
                SynthesizedInput(
                    input_id=f"in_{len(inputs) + 1:03d}_{vec_hash[:6]}",
                    args=args,
                    kwargs=kwargs,
                    instance_args=list(ia),
                    instance_kwargs=dict(ik),
                    source_strategy=strategy,
                    description=desc,
                )
            )

        required_pos = [p for p in pos_params if not p.has_default]
        required_kw = [p for p in kw_only_params if not p.has_default]

        if not required_pos and not required_kw:
            for iv in inst_variants:
                _add_vector([], {}, "defaults_only", "Zero-argument call exercising defaults", inst_override=iv)

        if pos_params or kw_only_params:
            baseline_pos = [param_pools[p.name][0] for p in required_pos]
            baseline_kw = {p.name: param_pools[p.name][0] for p in required_kw}
            for iv in inst_variants:
                _add_vector(
                    list(baseline_pos),
                    dict(baseline_kw),
                    "baseline_required",
                    "Baseline required arguments",
                    inst_override=iv,
                )

            full_baseline_pos = [param_pools[p.name][0] for p in pos_params]
            full_baseline_kw = {p.name: param_pools[p.name][0] for p in kw_only_params}
            max_pool_len = max((len(v) for v in param_pools.values()), default=0)

            for step in range(max_pool_len):
                for iv in inst_variants[:2]:
                    for idx, p in enumerate(required_pos):
                        if step < len(param_pools[p.name]):
                            args_copy = list(baseline_pos)
                            args_copy[idx] = param_pools[p.name][step]
                            _add_vector(
                                args_copy,
                                dict(baseline_kw),
                                "edge_sweep_required",
                                f"Sweep required param '{p.name}'",
                                inst_override=iv,
                            )

                    for idx, p in enumerate(pos_params):
                        if step < len(param_pools[p.name]):
                            args_slice = list(full_baseline_pos[: idx + 1])
                            args_slice[idx] = param_pools[p.name][step]
                            _add_vector(
                                args_slice,
                                dict(baseline_kw),
                                "edge_sweep_positional",
                                f"Sweep param '{p.name}'",
                                inst_override=iv,
                            )

                    for p in kw_only_params:
                        if step < len(param_pools[p.name]):
                            kw_copy = dict(full_baseline_kw)
                            kw_copy[p.name] = param_pools[p.name][step]
                            _add_vector(
                                list(baseline_pos),
                                kw_copy,
                                "edge_sweep_kwonly",
                                f"Sweep kwonly param '{p.name}'",
                                inst_override=iv,
                            )

            for step in range(min(max_pool_len, 24)):
                comb_args = [
                    param_pools[p.name][step % len(param_pools[p.name])]
                    for p in pos_params
                ]
                comb_kw = {
                    p.name: param_pools[p.name][step % len(param_pools[p.name])]
                    for p in kw_only_params
                }
                _add_vector(
                    comb_args,
                    comb_kw,
                    "combinatorial_property",
                    f"Combinatorial vector #{step + 1}",
                )
                if len(required_pos) < len(pos_params):
                    req_comb_args = [
                        param_pools[p.name][step % len(param_pools[p.name])]
                        for p in required_pos
                    ]
                    _add_vector(
                        req_comb_args,
                        dict(baseline_kw),
                        "combinatorial_required_only",
                        f"Combinatorial required-only vector #{step + 1}",
                    )

        if has_var_pos and not pos_params:
            for sample in ([], [1], [1, 2, 3], ["a", "b"], [None], [[]]):
                _add_vector(list(sample), {}, "varargs_probe", "Varargs probe")

        return inputs

    def _synthesize_stateful_chains(
        self,
        contract_v1: CallableContract,
        contract_v2: CallableContract,
        ast_consts: list[Any],
        rng: random.Random,
    ) -> list[SynthesizedInput]:
        """Synthesize 2-step and 3-step stateful method call chains on a shared class instance."""
        inst_variants = self._build_instance_variants(
            contract_v1.class_init_params, ast_consts, rng
        )
        inst_args, inst_kwargs = inst_variants[0]
        methods_v1 = {m["name"]: m["parameters"] for m in contract_v1.chain_methods}
        methods_v2 = {m["name"]: m["parameters"] for m in contract_v2.chain_methods}
        shared_names = sorted(set(methods_v1.keys()) & set(methods_v2.keys()))
        if not shared_names:
            return []

        diverse_seeds: list[Any] = ["a", b"a", "1.0.0", 0]
        method_arg_variants: dict[str, list[tuple[list[Any], dict[str, Any]]]] = {}
        for m_name in shared_names:
            raw_params = methods_v1[m_name]
            p_specs = [
                ParameterSpec(
                    name=p["name"],
                    kind=p["kind"],
                    annotation=p.get("annotation"),
                    has_default=bool(p.get("has_default", False)),
                    default_repr=p.get("default_repr"),
                    default_value_tagged=p.get("default_value_tagged"),
                )
                for p in raw_params
            ]
            req_pos = [
                p for p in p_specs if p.kind in ("POSITIONAL_ONLY", "POSITIONAL_OR_KEYWORD") and not p.has_default
            ]
            req_kw = [p for p in p_specs if p.kind == "KEYWORD_ONLY" and not p.has_default]

            variants: list[tuple[list[Any], dict[str, Any]]] = []
            for variant_idx in range(4):
                m_args: list[Any] = []
                m_kw: dict[str, Any] = {}
                for p_idx, p in enumerate(req_pos):
                    cands = _candidates_for_annotation(p.annotation, p.name, None, False, ast_consts, rng)
                    if variant_idx == 1 and p_idx == 0:
                        m_args.append(b"a")
                    elif variant_idx == 0:
                        m_args.append("a")
                    else:
                        m_args.append(cands[variant_idx % len(cands)] if cands else diverse_seeds[variant_idx])
                for p in req_kw:
                    cands = _candidates_for_annotation(p.annotation, p.name, None, False, ast_consts, rng)
                    m_kw[p.name] = cands[variant_idx % len(cands)] if cands else "a"
                variants.append((m_args, m_kw))
            method_arg_variants[m_name] = variants

        inputs: list[SynthesizedInput] = []
        seen_hashes: set[str] = set()
        cap = min(self.max_inputs_per_callable, 30)

        def _add_chain(chain: list[tuple[str, list[Any], dict[str, Any]]], desc: str) -> None:
            if len(inputs) >= cap:
                return
            h = _canonical_hash((inst_args, inst_kwargs, chain))
            if h in seen_hashes:
                return
            seen_hashes.add(h)
            inputs.append(
                SynthesizedInput(
                    input_id=f"chain_{len(inputs) + 1:03d}_{h[:6]}",
                    args=[],
                    kwargs={},
                    instance_args=list(inst_args),
                    instance_kwargs=dict(inst_kwargs),
                    method_chain=chain,
                    source_strategy="stateful_call_chain",
                    description=desc,
                )
            )

        mutator_prefixes = ("add", "set", "put", "push", "append", "insert", "extend", "update", "discard", "pop", "remove", "clear")
        prioritized = sorted(
            shared_names,
            key=lambda n: (0 if n.lower().startswith(mutator_prefixes) else 1, n),
        )

        for i, m1 in enumerate(prioritized):
            for j, m2 in enumerate(prioritized):
                for v_idx_1 in (0, 1):
                    v1_args, v1_kw = method_arg_variants[m1][v_idx_1 % len(method_arg_variants[m1])]
                    v2_args, v2_kw = method_arg_variants[m2][0]
                    _add_chain(
                        [(m1, v1_args, v1_kw), (m2, v2_args, v2_kw)],
                        f"Stateful 2-step chain: {m1}() -> {m2}()",
                    )
                if len(prioritized) >= 2:
                    m3 = prioritized[(i + j + 1) % len(prioritized)]
                    v1_args, v1_kw = method_arg_variants[m1][0]
                    v2_args, v2_kw = method_arg_variants[m2][(i + j) % len(method_arg_variants[m2])]
                    v3_args, v3_kw = method_arg_variants[m3][1 % len(method_arg_variants[m3])]
                    _add_chain(
                        [(m1, v1_args, v1_kw), (m2, v2_args, v2_kw), (m3, v3_args, v3_kw)],
                        f"Stateful 3-step chain: {m1}() -> {m2}() -> {m3}()",
                    )

        return inputs

    def _build_instance_variants(
        self,
        init_params: list[ParameterSpec],
        ast_consts: list[Any],
        rng: random.Random,
    ) -> list[tuple[list[Any], dict[str, Any]]]:
        base_args, base_kw = self._build_baseline_args(init_params, ast_consts, rng)
        variants: list[tuple[list[Any], dict[str, Any]]] = [(base_args, base_kw)]

        pos_init = [
            p for p in init_params if p.kind in ("POSITIONAL_ONLY", "POSITIONAL_OR_KEYWORD")
        ]
        if pos_init:
            first_p = pos_init[0]
            domain = _infer_domain_from_param_name(first_p.name)
            if domain and domain in _DOMAIN_POOLS:
                for cand in _DOMAIN_POOLS[domain][:2]:
                    alt_args = list(base_args)
                    if alt_args:
                        alt_args[0] = cand
                    else:
                        alt_args = [cand]
                    if (alt_args, base_kw) not in variants:
                        variants.append((alt_args, dict(base_kw)))
        return variants

    def _build_baseline_args(
        self,
        init_params: list[ParameterSpec],
        ast_consts: list[Any],
        rng: random.Random,
    ) -> tuple[list[Any], dict[str, Any]]:
        args: list[Any] = []
        kwargs: dict[str, Any] = {}
        for idx, p in enumerate(init_params):
            if p.has_default:
                # If the first init parameter defaults to an empty string but has a known domain (e.g. Specifier(spec="")),
                # supply a valid domain value so the instance constructs cleanly.
                def_val = decode_value(p.default_value_tagged)
                domain = _infer_domain_from_param_name(p.name)
                if idx == 0 and def_val == "" and domain in ("spec", "requirement", "version", "marker"):
                    args.append(_DOMAIN_POOLS[domain][0])
                continue
            cands = _candidates_for_annotation(
                p.annotation, p.name, None, False, ast_consts, rng
            )
            val = cands[0] if cands else "1.0.0"
            if p.kind in ("POSITIONAL_ONLY", "POSITIONAL_OR_KEYWORD"):
                args.append(val)
            elif p.kind == "KEYWORD_ONLY":
                kwargs[p.name] = val
        return args, kwargs
