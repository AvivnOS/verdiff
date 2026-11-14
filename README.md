# VerDiff — Automated Differential Fuzzing for Python Packages

**VerDiff** is an automated differential fuzzing engine that detects **Silent Breaking Changes** between any two versions of a Python package (`verdiff <package> <v1> <v2>`).

Static type checkers and API comparators only inspect function signatures. When a minor or patch release preserves its function signature (`def parse(text: str) -> Result`) while silently changing return values, raising new exception types on edge cases, mutating arguments or instances in-place, or introducing severe latency shifts, static tools report zero issues. **VerDiff** provisions both versions in isolated virtual environments, extracts their public API contracts, synthesizes type-aware and white-box AST-guided inputs (plus multi-step stateful method call chains), executes both versions side-by-side over an isolated JSON IPC bridge, filters out non-breaking internal sentinel/attribute noise, shrinks failing inputs to minimal counterexamples, and exports **100% standalone `pytest` regression suites** (zero `verdiff` runtime dependency).

---

## Core Architecture

1. **Isolated Dual-Environment Runner (`src/verdiff/env_manager.py`, `src/verdiff/worker.py`)**
   - Automatically provisions and caches isolated Python virtual environments under `.cache/envs/` via `uv` (with automatic `venv + pip` fallback).
   - Spawns persistent out-of-process worker subprocesses for `v1` and `v2` communicating over a sentinel-framed JSON/IPC protocol (`__VERDIFF_IPC__:`) that is immune to target libraries writing arbitrary output to `stdout`/`stderr`.
   - Enforces per-call wall-clock timeouts, deterministic PRNG and `os.urandom` seeding (`PYTHONHASHSEED=0`, `random.seed(42)`), outbound network socket blocking (`VERDIFF_ALLOW_NET=0`), and automatic worker restart after `os._exit` or native C-extension crashes.

2. **Public API Surface & Contract Extractor (`src/verdiff/extractor.py`, `src/verdiff/worker.py`)**
   - Combines runtime `inspect.signature` introspection with static `ast` module parsing across public submodules while deduplicating private submodule re-exports (`_structures`, `_collections`, etc.).
   - Prioritizes callables whose normalized AST body fingerprint or default parameters changed between `v1` and `v2`.
   - Separates static API changes (`removed`, `added`, `renamed`, `signature_changed`) from call-compatible targets eligible for behavioral fuzzing.

3. **White-Box, Edge-Case & Stateful Call-Chain Input Synthesizer (`src/verdiff/synthesizer.py`)**
   - Harvests string/numeric constants directly from target function AST bodies (`ast.Compare`, `ast.MatchValue`, default arguments) so branch guards are automatically exercised.
   - Generates deterministic edge-case pools across primitives and rich standard-library types (`None`, `bool`, boundary `int`/`float`/`nan`/`inf`/`-0.0`, ASCII/Unicode/RTL/SQL-injection/URL/semver strings, `bytes`, `datetime`, `Decimal`, `UUID`, `PurePath`, `re.Pattern`, nested collections).
   - **Stateful Call Chains (`<stateful_chain>`):** Synthesizes multi-step object lifecycles (instantiating a class with diverse constructor seeds and invoking 2–3 state-mutating methods sequentially) to expose in-place object state divergences.

4. **Behavioral Oracle, Smart `ObjectNoiseFilter` & Input Shrinker (`src/verdiff/oracle.py`)**
   - **Smart Noise Filter (`ObjectNoiseFilter`):** Eliminates false positives on custom objects by distinguishing genuine state/value breaks from:
     - *Backward-Compatible Attribute Additions:* When `v2` adds new public attributes/properties (e.g., `Retry.backoff_jitter` in `urllib3 2.0`) while every public attribute present in `v1` retains its exact value.
     - *Internal Sentinel Representation Changes:* When a library replaces bare `<object object at 0x...>` default sentinels with private enum tokens such as `<_TYPE_DEFAULT.token: -1>` (e.g., `urllib3.util.timeout.Timeout()`).
   - **4 Drift Categories:**
     - `return_value_drift` — Return value, type, or public object state changed.
     - `exception_type_drift` — `pass_to_fail` (`v1` returned, `v2` raised), `fail_to_pass` (`v1` raised, `v2` returned), `exception_class_changed`, or `crash_or_timeout`.
     - `input_mutation_drift` — In-place mutation of caller arguments (`args`/`kwargs`) or post-call instance state delta diverged between `v1` and `v2`.
     - `latency_regression` — Bidirectional `>= 3.0x` runtime shift above the minimum floor (`3.0ms`), confirmed via 5-run median benchmarking in both workers.
   - **Delta-Debugging Input Shrinker:** Automatically reduces complex inputs and multi-step method chains to the smallest minimal reproduction call.

5. **Pure Standalone Pytest & Report Generator (`src/verdiff/reporter.py`)**
   - Emits clean Markdown (`*_report.md`), self-contained dark-mode HTML (`*_report.html`), and **100% standalone `pytest` reproduction suites (`test_repro_*.py`)** using only Python stdlib + `pytest` (zero `verdiff` imports required in CI).

---

## Quick Start

### 1. One-Click Full Demo & Verification (Windows PowerShell)
Runs the core unit test suite (`tests/test_verdiff.py`), executes unfiltered differential fuzzing across **5 real PyPI upgrades** (Minor, Patch, and Major), and runs all generated standalone `pytest` reproduction suites:

```powershell
.\run_demo.ps1
```

### 2. CLI Usage

```bash
# Compare any two PyPI versions of a package (unfiltered full-package scan)
verdiff packaging 23.1 23.2

# Compare a patch release with custom input budget and latency threshold
verdiff sqlparse 0.4.3 0.4.4 --max-inputs 80 --latency-threshold 3.0 --output-dir ./reports

# Compare with an explicit cap on total reported drifts (--max-drifts 0 = unlimited default)
verdiff urllib3 2.0.2 2.0.7 --max-drifts 0 --max-drifts-per-callable 5
```

### CLI Options
- `--max-inputs <int>`: Maximum synthesized inputs per callable (default: `80`).
- `--max-drifts <int>`: Maximum total behavioral drifts to report across the package (`0` = unlimited, default: `0`).
- `--max-drifts-per-callable <int>`: Maximum distinct behavioral drifts recorded per callable signature (default: `5`).
- `--target-budget <float>`: Maximum wall-clock fuzzing budget in seconds per callable (default: `3.0`).
- `--latency-threshold <float>`: Minimum median runtime multiplier to flag a latency shift/regression (default: `3.0`).
- `--modules <mod ...>`: Optional submodule filter (omit for full unfiltered package scan).

---

## Verified Real-World PyPI Findings

See **[`FINDINGS.md`](FINDINGS.md)** for the complete forensic breakdown of all **71 real-world silent behavioral drifts** (and **161 filtered non-breaking object noise diffs**) discovered across 5 unfiltered PyPI upgrades:
1. **`packaging` (`23.0` -> `23.1`, Minor Control):** `0` behavioral drifts across `1,514` inputs (`0` false positives).
2. **`packaging` (`23.1` -> `23.2`, Minor):** `5` behavioral drifts (`Marker` trailing token rejection & `Requirement` URL validation shift).
3. **`sqlparse` (`0.4.3` -> `0.4.4`, Patch):** `22` behavioral drifts (`154x` regex backtracking latency shift on CVE-2023-30608, `Lexer.get_tokens` `AttributeError` `pass_to_fail`, and `'IN'` keyword reclassification across `tokenize`, `parse`, and `FilterStack.<stateful_chain>`).
4. **`urllib3` (`2.0.2` -> `2.0.7`, Patch):** `9` behavioral drifts (`Retry.remove_headers_on_redirect` silent `Cookie` header stripping for CVE-2023-43804 and `HTTPConnection.blocksize` doubling `8192 -> 16384`).
5. **`urllib3` (`1.26.18` -> `2.0.7`, Major):** `35` behavioral drifts (`HTTPHeaderDict.<stateful_chain>` and `HTTPHeaderDict.setdefault` `input_mutation_drift`, `HTTPHeaderDict.items` view object change, `HTTPResponse.read`), with `161` internal sentinel diffs (`Timeout()`) cleanly suppressed by `ObjectNoiseFilter`.

---

## Provenance & License

Built by **Vernal Forge** (`VerDiff — Silent Breaking Change Radar`).
Released under the [MIT License](LICENSE).
