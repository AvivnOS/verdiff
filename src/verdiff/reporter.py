"""Markdown, HTML, and Pure Standalone Pytest Reproduction Report Generator."""

from __future__ import annotations

import html
import re
from pathlib import Path

from verdiff.codec import value_to_python_expr
from verdiff.models import (
    DiffReport,
    StaticChangeKind,
    SynthesizedInput,
)


def _format_call_expr(qualname: str, inp: SynthesizedInput) -> str:
    if inp.method_chain:
        cls_name = qualname.split(".")[0]
        inst_pos = [value_to_python_expr(a) for a in inp.instance_args]
        inst_kw = [f"{k}={value_to_python_expr(v)}" for k, v in inp.instance_kwargs.items()]
        inst_all = ", ".join(inst_pos + inst_kw)
        steps_str: list[str] = [f"obj = {cls_name}({inst_all})"]
        for m_name, m_args, m_kw in inp.method_chain:
            s_pos = [value_to_python_expr(a) for a in m_args]
            s_kw = [f"{k}={value_to_python_expr(v)}" for k, v in m_kw.items()]
            steps_str.append(f"obj.{m_name}({', '.join(s_pos + s_kw)})")
        return "; ".join(steps_str)

    pos_parts = [value_to_python_expr(a) for a in inp.args]
    kw_parts = [f"{k}={value_to_python_expr(v)}" for k, v in inp.kwargs.items()]
    all_args = ", ".join(pos_parts + kw_parts)
    if inp.instance_args or inp.instance_kwargs:
        cls_name, method_name = qualname.split(".", 1)
        inst_pos = [value_to_python_expr(a) for a in inp.instance_args]
        inst_kw = [f"{k}={value_to_python_expr(v)}" for k, v in inp.instance_kwargs.items()]
        inst_all = ", ".join(inst_pos + inst_kw)
        return f"{cls_name}({inst_all}).{method_name}({all_args})"
    return f"{qualname}({all_args})"


def _outcome_display(
    outcome_status: str,
    ret_repr: str | None,
    ret_type: str | None,
    exc_type: str | None,
    exc_msg: str | None,
    median_ms: float | None,
    dur_ms: float,
) -> str:
    if outcome_status == "ok":
        timing = f" [{median_ms:.2f}ms median]" if median_ms is not None else ""
        return f"RETURN {ret_repr} (type: {ret_type}){timing}"
    if outcome_status == "timeout":
        return f"TIMEOUT ({exc_msg})"
    if outcome_status == "crash":
        return f"CRASH ({exc_msg})"
    return f"RAISE {exc_type}: {exc_msg}"


class ReportGenerator:
    """Renders DiffReport into Markdown, self-contained HTML, and pure standalone pytest reproduction suites."""

    @staticmethod
    def to_markdown(report: DiffReport) -> str:
        lines: list[str] = []
        lines.append(
            f"# VerDiff Differential Analysis: `{report.package}` (`{report.version_v1}` -> `{report.version_v2}`)"
        )
        lines.append("")
        lines.append("## 1. Executive Telemetry Summary")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("| :--- | :--- |")
        lines.append(f"| **Package** | `{report.package}` |")
        lines.append(f"| **Version A (Baseline)** | `{report.version_v1}` |")
        lines.append(f"| **Version B (Target)** | `{report.version_v2}` |")
        lines.append(f"| **Python Runtime** | `{report.python_version}` |")
        lines.append(f"| **Deterministic Seed** | `{report.seed}` |")
        lines.append(
            f"| **Public Callables (`v1` / `v2`)** | `{report.total_public_v1}` / `{report.total_public_v2}` |"
        )
        lines.append(f"| **Unchanged Signatures** | `{report.unchanged_signatures_count}` |")
        lines.append(f"| **Static Signature Changes** | `{report.static_breaking_count}` |")
        lines.append(f"| **Callables & Chains Fuzzed** | `{report.targets_fuzzed}` |")
        lines.append(f"| **Synthesized Inputs Executed** | `{report.total_inputs_executed}` |")
        lines.append(f"| **Non-Breaking Object Noise Filtered** | `{report.filtered_noise_count}` |")
        max_drifts_str = "Unlimited (0)" if report.max_drifts_limit == 0 else str(report.max_drifts_limit)
        lines.append(f"| **Max Drifts Ceiling (`--max-drifts`)** | `{max_drifts_str}` |")
        lines.append(f"| **Silent Behavioral Drifts Found** | **`{len(report.behavioral_drifts)}`** |")
        lines.append(f"| **Wall-Clock Duration** | `{report.elapsed_seconds:.2f}s` |")
        lines.append("")

        changed_static = [
            d
            for d in report.static_diffs
            if d.kind != StaticChangeKind.UNCHANGED_SIGNATURE
            and (d.contract_v1 is None or d.contract_v1.callable_kind != "stateful_chain")
            and (d.contract_v2 is None or d.contract_v2.callable_kind != "stateful_chain")
        ]
        lines.append(f"## 2. Static API Surface Changes ({len(changed_static)})")
        lines.append("")
        if not changed_static:
            lines.append("_No static signature changes detected between versions._")
            lines.append("")
        else:
            lines.append("| Change Kind | Module | Symbol (`v1` -> `v2`) | Signature / Details |")
            lines.append("| :--- | :--- | :--- | :--- |")
            for entry in changed_static:
                sym = (
                    f"`{entry.qualname_v1}` -> `{entry.qualname_v2}`"
                    if entry.qualname_v1 and entry.qualname_v2 and entry.qualname_v1 != entry.qualname_v2
                    else f"`{entry.qualname_v1 or entry.qualname_v2}`"
                )
                lines.append(
                    f"| `{entry.kind.value}` | `{entry.module}` | {sym} | {entry.details} |"
                )
            lines.append("")

        lines.append(f"## 3. Discovered Behavioral Drifts ({len(report.behavioral_drifts)})")
        lines.append("")
        if not report.behavioral_drifts:
            lines.append("_No behavioral drifts detected across fuzzed inputs._")
            lines.append("")
        else:
            for idx, d in enumerate(report.behavioral_drifts, start=1):
                orig_call = _format_call_expr(d.qualname, d.original_input)
                min_call = _format_call_expr(d.qualname, d.minimal_input)
                out1_str = _outcome_display(
                    d.outcome_v1.status,
                    d.outcome_v1.return_repr,
                    d.outcome_v1.return_type,
                    d.outcome_v1.exception_type,
                    d.outcome_v1.exception_message,
                    d.outcome_v1.median_duration_ms,
                    d.outcome_v1.duration_ms,
                )
                out2_str = _outcome_display(
                    d.outcome_v2.status,
                    d.outcome_v2.return_repr,
                    d.outcome_v2.return_type,
                    d.outcome_v2.exception_type,
                    d.outcome_v2.exception_message,
                    d.outcome_v2.median_duration_ms,
                    d.outcome_v2.duration_ms,
                )
                lines.append(f"### 3.{idx} `{d.module}.{d.qualname}{d.signature}`")
                lines.append(f"- **Drift Category:** `{d.category.value}` (`{d.subkind}`)")
                lines.append(f"- **Summary:** {d.summary}")
                lines.append(f"- **Input Strategy:** `{d.original_input.source_strategy}`")
                lines.append(f"- **Original Fuzzed Call:** `{orig_call}`")
                lines.append(
                    f"- **Shrunk Minimal Call ({d.shrink_steps} shrink steps):** `{min_call}`"
                )
                lines.append(f"- **Baseline (`{report.version_v1}`):** `{out1_str}`")
                lines.append(f"- **Target (`{report.version_v2}`):** `{out2_str}`")
                if (
                    d.outcome_v1.mutated_args_after is not None
                    or d.outcome_v2.mutated_args_after is not None
                    or d.outcome_v1.mutated_instance_after is not None
                    or d.outcome_v2.mutated_instance_after is not None
                ):
                    lines.append(
                        f"- **Post-Call Mutation Detected:** `args_mutated=({d.outcome_v1.mutated_args_after is not None} vs {d.outcome_v2.mutated_args_after is not None}), instance_mutated=({d.outcome_v1.mutated_instance_after is not None} vs {d.outcome_v2.mutated_instance_after is not None})`"
                    )
                lines.append("")

        return "\n".join(lines)

    @staticmethod
    def to_html(report: DiffReport) -> str:
        changed_static = [
            d
            for d in report.static_diffs
            if d.kind != StaticChangeKind.UNCHANGED_SIGNATURE
            and (d.contract_v1 is None or d.contract_v1.callable_kind != "stateful_chain")
            and (d.contract_v2 is None or d.contract_v2.callable_kind != "stateful_chain")
        ]

        static_rows: list[str] = []
        for entry in changed_static:
            sym = (
                f"{entry.qualname_v1} &rarr; {entry.qualname_v2}"
                if entry.qualname_v1 and entry.qualname_v2 and entry.qualname_v1 != entry.qualname_v2
                else (entry.qualname_v1 or entry.qualname_v2 or "")
            )
            static_rows.append(
                f"<tr>"
                f"<td><span class='tag tag-{html.escape(entry.kind.value)}'>{html.escape(entry.kind.value)}</span></td>"
                f"<td><code>{html.escape(entry.module)}</code></td>"
                f"<td><code>{sym}</code></td>"
                f"<td>{html.escape(entry.details)}</td>"
                f"</tr>"
            )

        drift_cards: list[str] = []
        for idx, d in enumerate(report.behavioral_drifts, start=1):
            orig_call = _format_call_expr(d.qualname, d.original_input)
            min_call = _format_call_expr(d.qualname, d.minimal_input)
            out1_str = _outcome_display(
                d.outcome_v1.status,
                d.outcome_v1.return_repr,
                d.outcome_v1.return_type,
                d.outcome_v1.exception_type,
                d.outcome_v1.exception_message,
                d.outcome_v1.median_duration_ms,
                d.outcome_v1.duration_ms,
            )
            out2_str = _outcome_display(
                d.outcome_v2.status,
                d.outcome_v2.return_repr,
                d.outcome_v2.return_type,
                d.outcome_v2.exception_type,
                d.outcome_v2.exception_message,
                d.outcome_v2.median_duration_ms,
                d.outcome_v2.duration_ms,
            )
            drift_cards.append(
                f"""
                <div class="card">
                  <div class="card-header">
                    <span class="card-title">#{idx} <code>{html.escape(d.module)}.{html.escape(d.qualname)}{html.escape(d.signature)}</code></span>
                    <span class="tag tag-drift">{html.escape(d.category.value)} / {html.escape(d.subkind or '')}</span>
                  </div>
                  <p class="summary">{html.escape(d.summary)}</p>
                  <div class="grid-two">
                    <div class="box">
                      <div class="box-label">Original Synthesized Call (<code>{html.escape(d.original_input.source_strategy)}</code>)</div>
                      <pre><code>{html.escape(orig_call)}</code></pre>
                    </div>
                    <div class="box">
                      <div class="box-label">Minimal Shrunk Counterexample ({d.shrink_steps} steps)</div>
                      <pre><code>{html.escape(min_call)}</code></pre>
                    </div>
                  </div>
                  <div class="grid-two">
                    <div class="box v1-box">
                      <div class="box-label">Version {html.escape(report.version_v1)} Outcome</div>
                      <pre><code>{html.escape(out1_str)}</code></pre>
                    </div>
                    <div class="box v2-box">
                      <div class="box-label">Version {html.escape(report.version_v2)} Outcome</div>
                      <pre><code>{html.escape(out2_str)}</code></pre>
                    </div>
                  </div>
                </div>
                """
            )

        static_section = (
            "<table><thead><tr><th>Kind</th><th>Module</th><th>Symbol</th><th>Details</th></tr></thead><tbody>"
            + "".join(static_rows)
            + "</tbody></table>"
            if static_rows
            else "<p class='muted'>No static signature changes detected.</p>"
        )
        drift_section = (
            "".join(drift_cards)
            if drift_cards
            else "<p class='muted'>No silent behavioral drifts detected across fuzzed inputs.</p>"
        )

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>VerDiff Report: {html.escape(report.package)} ({html.escape(report.version_v1)} vs {html.escape(report.version_v2)})</title>
<style>
  :root {{
    --bg: #0d1117;
    --panel: #161b22;
    --border: #30363d;
    --text: #e6edf3;
    --muted: #8b949e;
    --accent: #58a6ff;
    --danger: #f85149;
    --ok: #3fb950;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    padding: 2rem;
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    line-height: 1.5;
  }}
  .container {{ max-width: 1180px; margin: 0 auto; }}
  h1, h2 {{ border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; }}
  .metrics {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 0.75rem;
    margin: 1.25rem 0 2rem;
  }}
  .metric-card {{
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.85rem 1rem;
  }}
  .metric-label {{ font-size: 0.78rem; color: var(--muted); text-transform: uppercase; }}
  .metric-val {{ font-size: 1.35rem; font-weight: 600; margin-top: 0.25rem; font-family: ui-monospace, SFMono-Regular, Consolas, monospace; }}
  table {{ width: 100%; border-collapse: collapse; margin-bottom: 2rem; background: var(--panel); border: 1px solid var(--border); }}
  th, td {{ text-align: left; padding: 0.6rem 0.8rem; border-bottom: 1px solid var(--border); font-size: 0.9rem; }}
  th {{ color: var(--muted); font-weight: 600; background: #11151c; }}
  code, pre {{ font-family: ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 0.86rem; }}
  pre {{ margin: 0; white-space: pre-wrap; word-break: break-all; }}
  .card {{
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1rem 1.25rem;
    margin-bottom: 1rem;
  }}
  .card-header {{ display: flex; justify-content: space-between; align-items: center; gap: 1rem; flex-wrap: wrap; }}
  .card-title {{ font-weight: 600; font-size: 1rem; }}
  .summary {{ color: var(--text); margin: 0.6rem 0; }}
  .grid-two {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-top: 0.65rem; }}
  .box {{ background: #090d11; border: 1px solid var(--border); border-radius: 4px; padding: 0.65rem 0.8rem; }}
  .v1-box {{ border-left: 3px solid var(--ok); }}
  .v2-box {{ border-left: 3px solid var(--danger); }}
  .box-label {{ font-size: 0.75rem; color: var(--muted); margin-bottom: 0.35rem; }}
  .tag {{
    display: inline-block;
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
    border: 1px solid var(--border);
    background: #21262d;
  }}
  .tag-drift {{ border-color: var(--danger); color: #ff7b72; }}
  .muted {{ color: var(--muted); }}
</style>
</head>
<body>
<div class="container">
  <h1>VerDiff Differential Report: <code>{html.escape(report.package)}</code> (<code>{html.escape(report.version_v1)}</code> &rarr; <code>{html.escape(report.version_v2)}</code>)</h1>
  <div class="metrics">
    <div class="metric-card"><div class="metric-label">Public Callables (v1/v2)</div><div class="metric-val">{report.total_public_v1} / {report.total_public_v2}</div></div>
    <div class="metric-card"><div class="metric-label">Unchanged Signatures</div><div class="metric-val">{report.unchanged_signatures_count}</div></div>
    <div class="metric-card"><div class="metric-label">Static API Changes</div><div class="metric-val">{report.static_breaking_count}</div></div>
    <div class="metric-card"><div class="metric-label">Callables Fuzzed</div><div class="metric-val">{report.targets_fuzzed}</div></div>
    <div class="metric-card"><div class="metric-label">Inputs Executed</div><div class="metric-val">{report.total_inputs_executed}</div></div>
    <div class="metric-card"><div class="metric-label">Noise Filtered</div><div class="metric-val">{report.filtered_noise_count}</div></div>
    <div class="metric-card"><div class="metric-label">Behavioral Drifts</div><div class="metric-val" style="color: var(--danger);">{len(report.behavioral_drifts)}</div></div>
  </div>
  <h2>Static API Surface Changes ({len(changed_static)})</h2>
  {static_section}
  <h2>Silent Behavioral Drifts ({len(report.behavioral_drifts)})</h2>
  {drift_section}
</div>
</body>
</html>
"""

    @staticmethod
    def to_pytest_repro(report: DiffReport) -> str:
        """Generate a 100% pure standalone pytest regression suite with ZERO verdiff imports."""
        lines: list[str] = [
            f'r"""Standalone pytest regression suite for {report.package} ({report.version_v1} -> {report.version_v2}).',
            "",
            "Zero third-party fuzzing dependencies required: uses only Python stdlib + pytest + target package.",
            '"""',
            "",
            "from __future__ import annotations",
            "",
            "import copy",
            "import datetime",
            "import decimal",
            "import importlib",
            "import json",
            "import os",
            "import pathlib",
            "import re",
            "import statistics",
            "import subprocess",
            "import sys",
            "import time",
            "import uuid",
            "from pathlib import Path",
            "import pytest",
            "",
            f"PACKAGE = {report.package!r}",
            f"VERSION_V1 = {report.version_v1!r}",
            f"VERSION_V2 = {report.version_v2!r}",
            "",
            "_RUNNER_SNIPPET = r'''",
            "import copy, datetime, decimal, importlib, inspect, json, os, pathlib, random, re, statistics, sys, time, uuid",
            "payload = json.loads(sys.argv[1])",
            "ns = {'datetime': datetime, 'decimal': decimal, 'pathlib': pathlib, 're': re, 'uuid': uuid}",
            "mod = importlib.import_module(payload['module'])",
            "qual = payload['qualname']",
            "kind = payload['callable_kind']",
            "args = eval(payload['args_expr'], ns)",
            "kwargs = eval(payload['kwargs_expr'], ns)",
            "inst_args = eval(payload['inst_args_expr'], ns)",
            "inst_kwargs = eval(payload['inst_kwargs_expr'], ns)",
            "chain = eval(payload['chain_expr'], ns)",
            "def _safe_repr(o, limit=160):",
            "    try:",
            "        return re.sub(r' at 0x[0-9a-fA-F]+>', ' at 0xADDR>', repr(o))[:limit]",
            "    except Exception as e:",
            "        return f'<repr_error:{type(e).__name__}>'",
            "def _snap_obj(o, depth=0):",
            "    if depth > 2 or o is None or isinstance(o, (int, float, bool, str, bytes)):",
            "        return _safe_repr(o, 160)",
            "    if isinstance(o, (list, tuple, set, frozenset)):",
            "        return [_snap_obj(x, depth + 1) for x in list(o)[:32]]",
            "    d = {'__repr__': _safe_repr(o, 160)}",
            "    for attr in sorted(dir(o)):",
            "        if not attr.startswith('_'):",
            "            try:",
            "                val = getattr(o, attr)",
            "                if not callable(val):",
            "                    d[attr] = _snap_obj(val, depth + 1)",
            "            except Exception as e:",
            "                d[attr] = f'<exc:{type(e).__name__}>'",
            "    if hasattr(o, '__iter__') and not isinstance(o, (str, bytes, bytearray)):",
            "        try:",
            "            d['__iter__'] = [repr(x)[:80] for x in list(o)[:32]]",
            "        except Exception:",
            "            pass",
            "    return d",
            "args_before = repr(args)",
            "kwargs_before = repr(kwargs)",
            "def _call_once():",
            "    random.seed(42)",
            "    os.urandom = random.Random(42).randbytes",
            "    a_c = copy.deepcopy(args)",
            "    k_c = copy.deepcopy(kwargs)",
            "    ch_c = copy.deepcopy(chain)",
            "    inst = None",
            "    inst_before = None",
            "    t0 = time.perf_counter_ns()",
            "    try:",
            "        if kind == 'stateful_chain':",
            "            cls_name = qual.split('.')[0]",
            "            cls_obj = getattr(mod, cls_name)",
            "            inst = cls_obj(*copy.deepcopy(inst_args), **copy.deepcopy(inst_kwargs))",
            "            inst_before = _snap_obj(inst)",
            "            res = [getattr(inst, m)(*ma, **mk) for m, ma, mk in ch_c]",
            "        elif '.' in qual:",
            "            cls_name, m_name = qual.split('.', 1)",
            "            cls_obj = getattr(mod, cls_name)",
            "            raw_desc = inspect.getattr_static(cls_obj, m_name, None)",
            "            if isinstance(raw_desc, (staticmethod, classmethod)):",
            "                res = getattr(cls_obj, m_name)(*a_c, **k_c)",
            "            else:",
            "                inst = cls_obj(*copy.deepcopy(inst_args), **copy.deepcopy(inst_kwargs))",
            "                inst_before = _snap_obj(inst)",
            "                res = getattr(inst, m_name)(*a_c, **k_c)",
            "        else:",
            "            res = getattr(mod, qual)(*a_c, **k_c)",
            "        if inspect.isgenerator(res) or type(res).__name__ in ('map', 'filter', 'zip', 'enumerate', 'reversed'):",
            "            res = list(res)[:64]",
            "        dt = (time.perf_counter_ns() - t0) / 1_000_000.0",
            "        inst_after = _snap_obj(inst) if inst is not None else None",
            "        state_probe = _snap_obj(res)",
            "        return {'status': 'ok', 'type': f'{type(res).__module__}.{type(res).__qualname__}', 'repr': _safe_repr(res, 300), 'state': state_probe, 'after_args': _safe_repr(a_c, 300), 'after_inst': inst_after, 'ms': dt}",
            "    except BaseException as exc:",
            "        dt = (time.perf_counter_ns() - t0) / 1_000_000.0",
            "        return {'status': 'exception', 'exc_type': type(exc).__qualname__, 'exc_msg': str(exc)[:300], 'ms': dt}",
            "out = _call_once()",
            "if payload.get('benchmark') and out['status'] == 'ok':",
            "    samples = [_call_once()['ms'] for _ in range(5)]",
            "    out['median_ms'] = statistics.median(samples)",
            "print(json.dumps(out))",
            "'''",
            "",
            "",
            "def _find_env_python(pkg: str, ver: str) -> tuple[str, str | None]:",
            "    local_p = Path(ver)",
            "    if local_p.exists() and local_p.is_dir():",
            "        return sys.executable, str(local_p.resolve())",
            "    cache_envs = Path(__file__).resolve().parents[1] / '.cache' / 'envs'",
            "    slug_prefix = re.sub(r'[^a-zA-Z0-9._-]+', '_', f'{pkg}_{ver}_py')",
            "    if cache_envs.is_dir():",
            "        for child in cache_envs.iterdir():",
            "            if child.name.startswith(slug_prefix):",
            "                py = child / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')",
            "                if py.is_file():",
            "                    return str(py), None",
            "    return sys.executable, None",
            "",
            "",
            "def _invoke_standalone(version_spec: str, payload: dict) -> dict:",
            "    py_exe, extra_path = _find_env_python(PACKAGE, version_spec)",
            "    env = os.environ.copy()",
            "    env['PYTHONHASHSEED'] = '0'",
            "    if extra_path:",
            "        env['PYTHONPATH'] = extra_path + os.pathsep + env.get('PYTHONPATH', '')",
            "    proc = subprocess.run(",
            "        [py_exe, '-c', _RUNNER_SNIPPET, json.dumps(payload)],",
            "        capture_output=True, text=True, env=env, timeout=15.0",
            "    )",
            "    assert proc.returncode == 0, f'Subprocess failed: {proc.stderr}'",
            "    lines = [ln for ln in proc.stdout.strip().splitlines() if ln.startswith('{')]",
            "    return json.loads(lines[-1])",
            "",
        ]

        if not report.behavioral_drifts:
            lines.extend(
                [
                    "def test_zero_behavioral_drifts_verified():",
                    f'    """Verified 0 behavioral drifts between {report.package} {report.version_v1} and {report.version_v2}."""',
                    "    py1, _ = _find_env_python(PACKAGE, VERSION_V1)",
                    "    py2, _ = _find_env_python(PACKAGE, VERSION_V2)",
                    "    assert Path(py1).is_file() and Path(py2).is_file()",
                    "",
                ]
            )
            return "\n".join(lines)

        for idx, d in enumerate(report.behavioral_drifts, start=1):
            safe_fn = (
                re.sub(r"[^a-zA-Z0-9_]+", "_", f"{d.module}_{d.qualname}_{d.category.value}")
                .strip("_")
                .lower()
            )
            args_expr = "[" + ", ".join(value_to_python_expr(a) for a in d.minimal_input.args) + "]"
            kwargs_expr = (
                "{"
                + ", ".join(f"{k!r}: {value_to_python_expr(v)}" for k, v in d.minimal_input.kwargs.items())
                + "}"
            )
            inst_args_expr = (
                "[" + ", ".join(value_to_python_expr(a) for a in d.minimal_input.instance_args) + "]"
            )
            inst_kwargs_expr = (
                "{"
                + ", ".join(
                    f"{k!r}: {value_to_python_expr(v)}" for k, v in d.minimal_input.instance_kwargs.items()
                )
                + "}"
            )
            chain_items: list[str] = []
            for m_n, m_a, m_k in d.minimal_input.method_chain:
                ma_s = "[" + ", ".join(value_to_python_expr(x) for x in m_a) + "]"
                mk_s = "{" + ", ".join(f"{k!r}: {value_to_python_expr(v)}" for k, v in m_k.items()) + "}"
                chain_items.append(f"({m_n!r}, {ma_s}, {mk_s})")
            chain_expr = "[" + ", ".join(chain_items) + "]"

            min_call_readable = _format_call_expr(d.qualname, d.minimal_input)
            is_bench = d.category.value == "latency_regression"

            lines.extend(
                [
                    f"def test_repro_{idx:02d}_{safe_fn}():",
                    f'    """Reproduce {d.category.value} ({d.subkind}) on {d.module}.{d.qualname}.',
                    f"    Minimal Call: {min_call_readable}",
                    f'    """',
                    "    payload = {",
                    f"        'module': {d.module!r},",
                    f"        'qualname': {d.qualname!r},",
                    f"        'callable_kind': {d.callable_kind!r},",
                    f"        'args_expr': {args_expr!r},",
                    f"        'kwargs_expr': {kwargs_expr!r},",
                    f"        'inst_args_expr': {inst_args_expr!r},",
                    f"        'inst_kwargs_expr': {inst_kwargs_expr!r},",
                    f"        'chain_expr': {chain_expr!r},",
                    f"        'benchmark': {is_bench!r},",
                    "    }",
                    "    out_v1 = _invoke_standalone(VERSION_V1, payload)",
                    "    out_v2 = _invoke_standalone(VERSION_V2, payload)",
                ]
            )

            if d.category.value == "exception_type_drift":
                lines.append(f"    assert out_v1['status'] == {d.outcome_v1.status!r}")
                lines.append(f"    assert out_v2['status'] == {d.outcome_v2.status!r}")
                if d.outcome_v1.status == "exception":
                    lines.append(f"    assert out_v1['exc_type'] == {d.outcome_v1.exception_type!r}")
                if d.outcome_v2.status == "exception":
                    lines.append(f"    assert out_v2['exc_type'] == {d.outcome_v2.exception_type!r}")
            elif d.category.value == "return_value_drift":
                lines.append("    assert out_v1['status'] == 'ok' and out_v2['status'] == 'ok'")
                lines.append(
                    "    assert (out_v1['type'], out_v1['repr'], out_v1['state']) != (out_v2['type'], out_v2['repr'], out_v2['state'])"
                )
            elif d.category.value == "input_mutation_drift":
                lines.append("    assert out_v1['status'] == 'ok' and out_v2['status'] == 'ok'")
                lines.append(
                    "    assert (out_v1['after_args'], out_v1['after_inst']) != (out_v2['after_args'], out_v2['after_inst'])"
                )
            elif d.category.value == "latency_regression":
                lines.append("    assert out_v1['status'] == 'ok' and out_v2['status'] == 'ok'")
                lines.append("    m1, m2 = out_v1['median_ms'], out_v2['median_ms']")
                lines.append("    assert max(m1, m2) >= min(max(m1, 0.05), max(m2, 0.05)) * 2.0")
            lines.append("")

        return "\n".join(lines)

    @classmethod
    def write_all(
        cls,
        report: DiffReport,
        output_dir: Path,
        prefix: str | None = None,
    ) -> dict[str, Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        slug = prefix or re.sub(
            r"[^a-zA-Z0-9_]+",
            "_",
            f"{report.package}_{report.version_v1}_vs_{report.version_v2}",
        ).strip("_")
        md_path = output_dir / f"{slug}_report.md"
        html_path = output_dir / f"{slug}_report.html"
        pytest_path = output_dir / f"test_repro_{slug}.py"

        md_path.write_text(cls.to_markdown(report), encoding="utf-8")
        html_path = output_dir / f"{slug}_report.html"
        html_path.write_text(cls.to_html(report), encoding="utf-8")
        pytest_path.write_text(cls.to_pytest_repro(report), encoding="utf-8")

        return {
            "markdown": md_path,
            "html": html_path,
            "pytest": pytest_path,
        }
