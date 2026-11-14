"""Isolated Dual-Environment Runner & JSON-IPC Worker Manager."""

from __future__ import annotations

import json
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any

from verdiff.codec import encode_value
from verdiff.models import (
    CallableContract,
    ExecutionOutcome,
    ParameterSpec,
    SynthesizedInput,
)
from verdiff.worker import IPC_SENTINEL


def _sanitize_name(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "_", text.strip())


class WorkerClient:
    """Manages a persistent isolated Python worker process with timeout and crash recovery."""

    def __init__(
        self,
        python_exe: Path,
        worker_script: Path,
        sandbox_cwd: Path,
        extra_pythonpath: Path | None = None,
        default_timeout: float = 3.0,
    ) -> None:
        self.python_exe = python_exe
        self.worker_script = worker_script
        self.sandbox_cwd = sandbox_cwd
        self.extra_pythonpath = extra_pythonpath
        self.default_timeout = default_timeout
        self._proc: subprocess.Popen[str] | None = None
        self._resp_queue: queue.Queue[dict[str, Any] | None] = queue.Queue()
        self._reader_thread: threading.Thread | None = None

    def start(self) -> None:
        if self._proc is not None and self._proc.poll() is None:
            return

        self.sandbox_cwd.mkdir(parents=True, exist_ok=True)
        self._resp_queue = queue.Queue()

        env = os.environ.copy()
        env["PYTHONHASHSEED"] = "0"
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"
        if self.extra_pythonpath is not None:
            existing_pp = env.get("PYTHONPATH", "")
            env["PYTHONPATH"] = (
                f"{self.extra_pythonpath}{os.pathsep}{existing_pp}"
                if existing_pp
                else str(self.extra_pythonpath)
            )

        self._proc = subprocess.Popen(
            [str(self.python_exe), "-u", str(self.worker_script)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(self.sandbox_cwd),
            env=env,
            bufsize=1,
        )
        self._reader_thread = threading.Thread(
            target=self._stdout_reader,
            args=(self._proc, self._resp_queue),
            daemon=True,
        )
        self._reader_thread.start()

    @staticmethod
    def _stdout_reader(
        proc: subprocess.Popen[str],
        out_q: queue.Queue[dict[str, Any] | None],
    ) -> None:
        assert proc.stdout is not None
        try:
            for line in proc.stdout:
                if line.startswith(IPC_SENTINEL):
                    payload_str = line[len(IPC_SENTINEL) :].strip()
                    try:
                        out_q.put(json.loads(payload_str))
                    except Exception as exc:
                        out_q.put({"ok": False, "error": f"IPC JSON decode error: {exc}"})
        except Exception:
            pass
        finally:
            out_q.put(None)

    def kill(self) -> None:
        if self._proc is not None:
            try:
                self._proc.kill()
                self._proc.wait(timeout=2.0)
            except Exception:
                pass
            self._proc = None

    def close(self) -> None:
        if self._proc is not None and self._proc.poll() is None:
            try:
                assert self._proc.stdin is not None
                self._proc.stdin.write(json.dumps({"cmd": "quit"}) + "\n")
                self._proc.stdin.flush()
                self._proc.wait(timeout=1.5)
            except Exception:
                pass
        self.kill()

    def request(self, payload: dict[str, Any], timeout: float | None = None) -> dict[str, Any]:
        wait_sec = timeout if timeout is not None else self.default_timeout
        self.start()
        assert self._proc is not None and self._proc.stdin is not None

        while not self._resp_queue.empty():
            try:
                self._resp_queue.get_nowait()
            except queue.Empty:
                break

        try:
            self._proc.stdin.write(json.dumps(payload) + "\n")
            self._proc.stdin.flush()
        except Exception as exc:
            self.kill()
            return {"ok": False, "status": "crash", "error": f"Worker stdin write failed: {exc}"}

        try:
            resp = self._resp_queue.get(timeout=wait_sec)
        except queue.Empty:
            self.kill()
            return {"ok": False, "status": "timeout", "error": f"Execution timed out after {wait_sec:.2f}s"}

        if resp is None:
            exit_code = self._proc.poll() if self._proc else -1
            self.kill()
            return {
                "ok": False,
                "status": "crash",
                "error": f"Worker process terminated unexpectedly (exit code {exit_code})",
            }

        return resp

    def extract_surface(
        self, package_name: str, modules: list[str] | None = None
    ) -> list[CallableContract]:
        resp = self.request(
            {"cmd": "extract", "package": package_name, "modules": modules},
            timeout=30.0,
        )
        if not resp.get("ok"):
            raise RuntimeError(f"Failed to extract API surface for {package_name}: {resp.get('error')}")

        contracts: list[CallableContract] = []
        for raw_c in resp["data"].get("contracts", []):
            params = [
                ParameterSpec(
                    name=p["name"],
                    kind=p["kind"],
                    annotation=p.get("annotation"),
                    has_default=bool(p.get("has_default", False)),
                    default_repr=p.get("default_repr"),
                    default_value_tagged=p.get("default_value_tagged"),
                )
                for p in raw_c.get("parameters", [])
            ]
            init_params = [
                ParameterSpec(
                    name=p["name"],
                    kind=p["kind"],
                    annotation=p.get("annotation"),
                    has_default=bool(p.get("has_default", False)),
                    default_repr=p.get("default_repr"),
                    default_value_tagged=p.get("default_value_tagged"),
                )
                for p in raw_c.get("class_init_params", [])
            ]
            contracts.append(
                CallableContract(
                    qualname=raw_c["qualname"],
                    module=raw_c["module"],
                    callable_kind=raw_c["callable_kind"],
                    parameters=params,
                    return_annotation=raw_c.get("return_annotation"),
                    docstring_summary=raw_c.get("docstring_summary"),
                    ast_constants=raw_c.get("ast_constants", []),
                    raised_exceptions=raw_c.get("raised_exceptions", []),
                    body_ast_fingerprint=raw_c.get("body_ast_fingerprint", ""),
                    class_init_params=init_params,
                    chain_methods=raw_c.get("chain_methods", []),
                )
            )
        return contracts

    @staticmethod
    def _encode_method_chain(
        method_chain: list[tuple[str, list[Any], dict[str, Any]]]
    ) -> list[list[Any]]:
        encoded: list[list[Any]] = []
        for m_name, m_args, m_kw in method_chain:
            encoded.append(
                [
                    m_name,
                    [encode_value(a) for a in m_args],
                    {k: encode_value(v) for k, v in m_kw.items()},
                ]
            )
        return encoded

    def execute_callable(
        self,
        contract: CallableContract,
        synth_input: SynthesizedInput,
        timeout: float | None = None,
    ) -> ExecutionOutcome:
        payload = {
            "cmd": "execute",
            "module": contract.module,
            "qualname": contract.qualname,
            "callable_kind": contract.callable_kind,
            "args": [encode_value(a) for a in synth_input.args],
            "kwargs": {k: encode_value(v) for k, v in synth_input.kwargs.items()},
            "instance_args": [encode_value(a) for a in synth_input.instance_args],
            "instance_kwargs": {k: encode_value(v) for k, v in synth_input.instance_kwargs.items()},
            "method_chain": self._encode_method_chain(synth_input.method_chain),
        }
        resp = self.request(payload, timeout=timeout)
        if not resp.get("ok"):
            status = resp.get("status", "crash")
            return ExecutionOutcome(
                status=status if status in ("timeout", "crash") else "crash",
                exception_type="TimeoutError" if status == "timeout" else "WorkerCrashError",
                exception_module="builtins",
                exception_message=resp.get("error", "Unknown worker error"),
            )

        out = resp["outcome"]
        return ExecutionOutcome(
            status=out["status"],
            return_type=out.get("return_type"),
            return_repr=out.get("return_repr"),
            return_canonical=out.get("return_canonical"),
            exception_type=out.get("exception_type"),
            exception_module=out.get("exception_module"),
            exception_message=out.get("exception_message"),
            mutated_args_after=out.get("mutated_args_after"),
            mutated_kwargs_after=out.get("mutated_kwargs_after"),
            mutated_instance_after=out.get("mutated_instance_after"),
            duration_ms=float(out.get("duration_ms", 0.0)),
        )

    def benchmark_callable(
        self,
        contract: CallableContract,
        synth_input: SynthesizedInput,
        repeats: int = 5,
    ) -> float | None:
        payload = {
            "cmd": "benchmark",
            "module": contract.module,
            "qualname": contract.qualname,
            "callable_kind": contract.callable_kind,
            "args": [encode_value(a) for a in synth_input.args],
            "kwargs": {k: encode_value(v) for k, v in synth_input.kwargs.items()},
            "instance_args": [encode_value(a) for a in synth_input.instance_args],
            "instance_kwargs": {k: encode_value(v) for k, v in synth_input.instance_kwargs.items()},
            "method_chain": self._encode_method_chain(synth_input.method_chain),
            "repeats": repeats,
        }
        resp = self.request(payload, timeout=max(10.0, self.default_timeout * repeats))
        if not resp.get("ok"):
            return None
        bench = resp.get("benchmark", {})
        if bench.get("status") != "ok":
            return None
        return float(bench.get("median_duration_ms", 0.0))


class IsolatedEnvManager:
    """Provisions and caches isolated virtual environments for package version A and version B."""

    def __init__(
        self,
        cache_root: Path | None = None,
        python_spec: str = "3.12",
        timeout_per_call: float = 2.5,
    ) -> None:
        project_root = Path(__file__).resolve().parents[2]
        self.cache_root = cache_root or (project_root / ".cache")
        self.envs_dir = self.cache_root / "envs"
        self.pkg_cache_dir = self.cache_root / "pkg_cache"
        self.sandbox_cwd = self.cache_root / "sandbox_cwd"
        self.python_spec = python_spec
        self.timeout_per_call = timeout_per_call
        self.worker_script = Path(__file__).resolve().parent / "worker.py"

        self.envs_dir.mkdir(parents=True, exist_ok=True)
        self.pkg_cache_dir.mkdir(parents=True, exist_ok=True)
        self.sandbox_cwd.mkdir(parents=True, exist_ok=True)

    def _build_env_vars(self) -> dict[str, str]:
        env = os.environ.copy()
        env["UV_CACHE_DIR"] = str(self.pkg_cache_dir / "uv")
        env["PIP_CACHE_DIR"] = str(self.pkg_cache_dir / "pip")
        env["PYTHONUTF8"] = "1"
        return env

    @staticmethod
    def _venv_python_path(venv_dir: Path) -> Path:
        if os.name == "nt":
            return venv_dir / "Scripts" / "python.exe"
        return venv_dir / "bin" / "python"

    def ensure_environment(self, package: str, version: str) -> WorkerClient:
        local_dir = Path(version)
        if local_dir.exists() and local_dir.is_dir():
            return WorkerClient(
                python_exe=Path(sys.executable),
                worker_script=self.worker_script,
                sandbox_cwd=self.sandbox_cwd,
                extra_pythonpath=local_dir.resolve(),
                default_timeout=self.timeout_per_call,
            )

        env_slug = f"{_sanitize_name(package)}_{_sanitize_name(version)}_py{_sanitize_name(self.python_spec)}"
        venv_dir = self.envs_dir / env_slug
        py_exe = self._venv_python_path(venv_dir)
        marker_file = venv_dir / ".verdiff_ready"

        if not (py_exe.is_file() and marker_file.is_file()):
            self._provision_venv(venv_dir, py_exe, package, version)
            marker_file.write_text(f"{package}=={version}\n", encoding="utf-8")

        return WorkerClient(
            python_exe=py_exe,
            worker_script=self.worker_script,
            sandbox_cwd=self.sandbox_cwd,
            default_timeout=self.timeout_per_call,
        )

    def _provision_venv(self, venv_dir: Path, py_exe: Path, package: str, version: str) -> None:
        env = self._build_env_vars()
        uv_bin = shutil.which("uv")

        if venv_dir.exists():
            shutil.rmtree(venv_dir, ignore_errors=True)

        spec = f"{package}=={version}"
        if uv_bin:
            cmd_venv = [uv_bin, "venv", str(venv_dir), "--python", self.python_spec]
            res = subprocess.run(cmd_venv, env=env, capture_output=True, text=True)
            if res.returncode != 0:
                cmd_venv = [uv_bin, "venv", str(venv_dir), "--python", sys.executable]
                subprocess.run(cmd_venv, env=env, check=True, capture_output=True, text=True)

            cmd_install = [
                uv_bin,
                "pip",
                "install",
                "--python",
                str(py_exe),
                spec,
            ]
            install_res = subprocess.run(cmd_install, env=env, capture_output=True, text=True)
            if install_res.returncode != 0:
                raise RuntimeError(
                    f"uv pip install failed for {spec}:\n{install_res.stderr or install_res.stdout}"
                )
        else:
            subprocess.run(
                [sys.executable, "-m", "venv", str(venv_dir)],
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                [str(py_exe), "-m", "pip", "install", "--disable-pip-version-check", spec],
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )
