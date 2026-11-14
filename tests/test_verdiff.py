"""Comprehensive unit and integration test suite for VerDiff."""

from __future__ import annotations

import datetime
import decimal
import math
import pathlib
import re
import subprocess
import sys
import uuid
from pathlib import Path

import pytest

from verdiff.codec import (
    decode_value,
    encode_value,
    strip_memory_addresses,
    value_to_python_expr,
)
from verdiff.engine import VerDiffEngine
from verdiff.env_manager import WorkerClient
from verdiff.models import (
    CallableContract,
    DriftCategory,
    StaticChangeKind,
    SynthesizedInput,
)
from verdiff.reporter import ReportGenerator


class _SampleSlotted:
    __slots__ = ("public_slot", "_private_slot")

    def __init__(self, pub: int, priv: int) -> None:
        self.public_slot = pub
        self._private_slot = priv

    @property
    def computed(self) -> int:
        return self.public_slot * 2


def test_codec_roundtrip_and_canonicalization() -> None:
    samples = [
        None,
        True,
        False,
        0,
        -42,
        2**62,
        0.0,
        -0.0,
        3.14159,
        float("inf"),
        float("-inf"),
        float("nan"),
        "",
        "שלום עולם \u202eRTL\u202c",
        b"\x00\xff\xfe",
        bytearray(b"abc"),
        [1, "two", None],
        (1, 2, 3),
        (99,),
        {"x", "y"},
        frozenset([1, 2]),
        {"k1": [1, 2], "k2": {"nested": True}},
        datetime.date(2026, 11, 13),
        datetime.datetime(2026, 11, 13, 19, 0, 0),
        datetime.timedelta(days=2, seconds=30, microseconds=500),
        decimal.Decimal("19.99"),
        pathlib.Path("sandbox/test.txt"),
        uuid.UUID("12345678-1234-5678-1234-567812345678"),
        re.compile(r"^[a-z]+$", re.IGNORECASE),
        slice(1, 10, 2),
    ]

    for val in samples:
        encoded = encode_value(val)
        decoded = decode_value(encoded)
        expr = value_to_python_expr(val)
        eval_val = eval(expr, {"datetime": datetime, "decimal": decimal, "pathlib": pathlib, "uuid": uuid, "re": re})

        if isinstance(val, float) and math.isnan(val):
            assert isinstance(decoded, float) and math.isnan(decoded)
            assert isinstance(eval_val, float) and math.isnan(eval_val)
        elif isinstance(val, float) and val == 0.0:
            assert math.copysign(1.0, decoded) == math.copysign(1.0, val)
            assert math.copysign(1.0, eval_val) == math.copysign(1.0, val)
        else:
            assert type(decoded) is type(val) or isinstance(val, pathlib.PurePath)
            assert decoded == val
            assert eval_val == val

    # Verify private slot differences do not trigger false-positive state mismatch
    obj1 = _SampleSlotted(10, 111)
    obj2 = _SampleSlotted(10, 999)
    assert encode_value(obj1) == encode_value(obj2)

    # Verify memory address stripping
    raw_repr = "<CustomObject at 0x000001F9A2B3C4D0>"
    assert strip_memory_addresses(raw_repr) == "<CustomObject at 0xADDR>"


@pytest.fixture()
def synthetic_pkg_versions(tmp_path: Path) -> tuple[Path, Path]:
    """Create two isolated synthetic package versions on disk to test all static & behavioral diffs."""
    v1_dir = tmp_path / "v1"
    v2_dir = tmp_path / "v2"
    (v1_dir / "synthpkg").mkdir(parents=True)
    (v2_dir / "synthpkg").mkdir(parents=True)

    v1_code = '''"""Synthetic package v1 for VerDiff testing."""
import time

def parse_code(token: str) -> dict:
    """Parse a token string."""
    if token == "":
        return {"valid": False, "empty": True}
    if token == "MAGIC_SECRET":
        return {"valid": True, "role": "user"}
    if not token.isalnum():
        raise KeyError("Non-alphanumeric token")
    return {"valid": True, "token": token}

def normalize_items(items: list) -> list:
    """Return sorted items without mutating caller list in v1."""
    return sorted(str(x) for x in items)

def old_helper(x: int, y: int = 1) -> int:
    """Helper that will be renamed in v2."""
    return (x * 3) + y

def removed_in_v2(flag: bool) -> str:
    return "yes" if flag else "no"

def config_connect(host: str, retries: int = 3) -> str:
    return f"{host}:{retries}"

def heavy_digest(payload: str) -> int:
    return len(payload)
'''

    v2_code = '''"""Synthetic package v2 with silent breaking changes and static diffs."""
import time

def parse_code(token: str) -> dict:
    """Parse a token string (v2 introduces silent breaking changes)."""
    if token == "":
        raise ValueError("Empty token is no longer allowed in v2")
    if token == "MAGIC_SECRET":
        return {"valid": True, "role": "admin"}
    if not token.isalnum():
        raise ValueError("Non-alphanumeric token now raises ValueError instead of KeyError")
    return {"valid": True, "token": token}

def normalize_items(items: list) -> list:
    """Silently mutates caller list in-place in v2!"""
    items.clear()
    items.append("mutated_in_place")
    return ["mutated_in_place"]

def renamed_helper(x: int, y: int = 1) -> int:
    """Renamed from old_helper with identical AST body."""
    return (x * 3) + y

def added_in_v2(name: str) -> str:
    return name.upper()

def config_connect(host: str, retries: int = 5, timeout: float = 10.0) -> str:
    return f"{host}:{retries}"

def heavy_digest(payload: str) -> int:
    time.sleep(0.012)
    return len(payload)
'''

    (v1_dir / "synthpkg" / "__init__.py").write_text(v1_code, encoding="utf-8")
    (v2_dir / "synthpkg" / "__init__.py").write_text(v2_code, encoding="utf-8")
    return v1_dir, v2_dir


def test_end_to_end_synthetic_package_diffs_and_reports(
    synthetic_pkg_versions: tuple[Path, Path],
    tmp_path: Path,
) -> None:
    v1_dir, v2_dir = synthetic_pkg_versions
    cache_dir = tmp_path / "cache"
    out_dir = tmp_path / "reports"

    engine = VerDiffEngine(
        cache_root=cache_dir,
        seed=42,
        max_inputs_per_callable=30,
        latency_threshold=3.0,
        min_latency_floor_ms=4.0,
    )
    report = engine.run("synthpkg", str(v1_dir), str(v2_dir))

    # 1. Verify Static API Surface Diffs
    static_by_kind = {}
    for entry in report.static_diffs:
        static_by_kind.setdefault(entry.kind, []).append(entry)

    assert StaticChangeKind.RENAMED in static_by_kind
    renamed = static_by_kind[StaticChangeKind.RENAMED][0]
    assert renamed.qualname_v1 == "old_helper"
    assert renamed.qualname_v2 == "renamed_helper"

    assert StaticChangeKind.REMOVED in static_by_kind
    assert any(e.qualname_v1 == "removed_in_v2" for e in static_by_kind[StaticChangeKind.REMOVED])

    assert StaticChangeKind.ADDED in static_by_kind
    assert any(e.qualname_v2 == "added_in_v2" for e in static_by_kind[StaticChangeKind.ADDED])

    assert StaticChangeKind.SIGNATURE_CHANGED in static_by_kind
    assert any(e.qualname_v1 == "config_connect" for e in static_by_kind[StaticChangeKind.SIGNATURE_CHANGED])

    # 2. Verify all 4 Behavioral Drift Categories are caught
    categories_found = {d.category for d in report.behavioral_drifts}
    assert DriftCategory.RETURN_VALUE_DRIFT in categories_found
    assert DriftCategory.EXCEPTION_TYPE_DRIFT in categories_found
    assert DriftCategory.INPUT_MUTATION_DRIFT in categories_found
    assert DriftCategory.LATENCY_REGRESSION in categories_found

    # Check white-box AST constant seeding caught MAGIC_SECRET return value drift
    parse_drifts = [d for d in report.behavioral_drifts if d.qualname == "parse_code"]
    assert any(d.category == DriftCategory.RETURN_VALUE_DRIFT for d in parse_drifts)
    assert any(d.subkind == "pass_to_fail" for d in parse_drifts)
    assert any(d.subkind == "exception_class_changed" for d in parse_drifts)

    # 3. Verify Report Generation & Auto-Exported Pytest Reproduction Suite
    paths = ReportGenerator.write_all(report, output_dir=out_dir, prefix="synthpkg_diff")
    assert paths["markdown"].is_file()
    assert paths["html"].is_file()
    assert paths["pytest"].is_file()

    md_text = paths["markdown"].read_text(encoding="utf-8")
    assert "return_value_drift" in md_text
    assert "input_mutation_drift" in md_text
    assert "latency_regression" in md_text

    # Run the generated pytest reproduction file directly to prove it passes!
    res = subprocess.run(
        [sys.executable, "-m", "pytest", str(paths["pytest"]), "-q"],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"Generated repro test failed:\n{res.stdout}\n{res.stderr}"


def test_worker_timeout_and_crash_isolation(tmp_path: Path) -> None:
    pkg_dir = tmp_path / "crashpkg_root"
    (pkg_dir / "crashpkg").mkdir(parents=True)
    (pkg_dir / "crashpkg" / "__init__.py").write_text(
        """
import os
import time

def hang_if_negative(x: int) -> int:
    if x < 0:
        time.sleep(5.0)
    if x == 999:
        os._exit(1)
    return x + 1
""",
        encoding="utf-8",
    )

    worker_script = Path(__file__).resolve().parents[1] / "src" / "verdiff" / "worker.py"
    client = WorkerClient(
        python_exe=Path(sys.executable),
        worker_script=worker_script,
        sandbox_cwd=tmp_path / "sandbox",
        extra_pythonpath=pkg_dir,
        default_timeout=0.4,
    )
    contract = CallableContract(qualname="hang_if_negative", module="crashpkg", callable_kind="function")

    try:
        # 1. Timeout recovery
        out_timeout = client.execute_callable(
            contract, SynthesizedInput(input_id="t1", args=[-1], kwargs={})
        )
        assert out_timeout.status == "timeout"

        # 2. Hard process crash recovery
        out_crash = client.execute_callable(
            contract, SynthesizedInput(input_id="t2", args=[999], kwargs={})
        )
        assert out_crash.status == "crash"

        # 3. Subsequent normal execution works seamlessly on respawned worker
        out_ok = client.execute_callable(
            contract, SynthesizedInput(input_id="t3", args=[10], kwargs={})
        )
        assert out_ok.status == "ok"
        assert out_ok.return_repr == "11"
    finally:
        client.close()


def test_stdout_noise_immunity_and_deterministic_seed(tmp_path: Path) -> None:
    """Verify that target functions writing raw text to sys.stdout do not corrupt JSON IPC."""
    v1_dir = tmp_path / "noisy_v1"
    v2_dir = tmp_path / "noisy_v2"
    (v1_dir / "noisypkg").mkdir(parents=True)
    (v2_dir / "noisypkg").mkdir(parents=True)

    (v1_dir / "noisypkg" / "__init__.py").write_text(
        """
import sys

def noisy_calc(text: str, count: int = 1) -> str:
    print("RAW STDOUT NOISE LINE 1")
    sys.stdout.write("UNTERMINATED NOISE ")
    sys.stderr.write("STDERR NOISE\\n")
    return text * count
""",
        encoding="utf-8",
    )
    (v2_dir / "noisypkg" / "__init__.py").write_text(
        """
import sys

def noisy_calc(text: str, count: int = 1) -> str:
    print("DIFFERENT STDOUT NOISE")
    if count < 0:
        raise ValueError("Negative count disallowed in v2")
    return text * count
""",
        encoding="utf-8",
    )

    engine1 = VerDiffEngine(cache_root=tmp_path / "cache", seed=99, max_inputs_per_callable=20)
    engine2 = VerDiffEngine(cache_root=tmp_path / "cache", seed=99, max_inputs_per_callable=20)

    rep1 = engine1.run("noisypkg", str(v1_dir), str(v2_dir))
    rep2 = engine2.run("noisypkg", str(v1_dir), str(v2_dir))

    assert len(rep1.behavioral_drifts) == 1
    assert rep1.behavioral_drifts[0].category == DriftCategory.EXCEPTION_TYPE_DRIFT
    assert rep1.behavioral_drifts[0].subkind == "pass_to_fail"
    # Verify deterministic seed produces identical minimal counterexamples
    assert rep1.behavioral_drifts[0].minimal_input.args == rep2.behavioral_drifts[0].minimal_input.args


def test_input_shrinker_reduces_complex_input(tmp_path: Path) -> None:
    """Verify that a long string/list input triggering a drift is shrunk to a minimal counterexample."""
    v1_dir = tmp_path / "shrink_v1"
    v2_dir = tmp_path / "shrink_v2"
    (v1_dir / "shrinkpkg").mkdir(parents=True)
    (v2_dir / "shrinkpkg").mkdir(parents=True)

    (v1_dir / "shrinkpkg" / "__init__.py").write_text(
        """
def process_batch(items: list[int]) -> int:
    return sum(items)
""",
        encoding="utf-8",
    )
    (v2_dir / "shrinkpkg" / "__init__.py").write_text(
        """
def process_batch(items: list[int]) -> int:
    if len(items) > 0:
        return sum(items) + 100
    return 0
""",
        encoding="utf-8",
    )

    engine = VerDiffEngine(cache_root=tmp_path / "cache", seed=42, max_inputs_per_callable=15)
    report = engine.run("shrinkpkg", str(v1_dir), str(v2_dir))

    assert len(report.behavioral_drifts) == 1
    drift = report.behavioral_drifts[0]
    assert drift.category == DriftCategory.RETURN_VALUE_DRIFT
    # Original input was [1, 2, 3]; shrunk input should have length 1 and element 0 -> [0]
    assert len(drift.minimal_input.args[0]) == 1
    assert drift.minimal_input.args[0] == [0]
    assert drift.shrink_steps >= 1


def test_object_noise_filter_and_stateful_call_chains(tmp_path: Path) -> None:
    """Verify ObjectNoiseFilter suppresses backward-compatible attribute additions and sentinels,
    while Stateful Call Chains catch multi-step instance mutation drifts and standalone pytest has zero verdiff imports.
    """
    v1_dir = tmp_path / "state_v1"
    v2_dir = tmp_path / "state_v2"
    (v1_dir / "statepkg").mkdir(parents=True)
    (v2_dir / "statepkg").mkdir(parents=True)

    (v1_dir / "statepkg" / "__init__.py").write_text(
        """
_SENTINEL_V1 = object()

class ConfigBox:
    def __init__(self, timeout=_SENTINEL_V1):
        self.timeout = None if timeout is _SENTINEL_V1 else timeout
        self._raw = timeout

    def __repr__(self) -> str:
        return f"ConfigBox(timeout={self._raw!r})"

class TokenBuffer:
    def __init__(self) -> None:
        self.items: list[str] = []

    def push(self, val: str) -> int:
        self.items.append(val)
        return len(self.items)

    def compact(self, prefix: str = "") -> int:
        # In v1, compact keeps all non-empty items
        self.items = [x for x in self.items if x != ""]
        return len(self.items)
""",
        encoding="utf-8",
    )

    (v2_dir / "statepkg" / "__init__.py").write_text(
        """
import enum

class _TYPE_DEFAULT(enum.Enum):
    token = -1

class ConfigBox:
    def __init__(self, timeout=_TYPE_DEFAULT.token):
        self.timeout = None if timeout is _TYPE_DEFAULT.token else timeout
        self.new_backward_compat_attr = 42
        self._raw = timeout

    def __repr__(self) -> str:
        return f"ConfigBox(timeout={self._raw!r})"

class TokenBuffer:
    def __init__(self) -> None:
        self.items: list[str] = []

    def push(self, val: str) -> int:
        self.items.append(val)
        return len(self.items)

    def compact(self, prefix: str = "") -> int:
        # In v2, compact silently clears the entire buffer!
        self.items.clear()
        self.items.append("MUTATED_BY_V2")
        return 0
""",
        encoding="utf-8",
    )

    engine = VerDiffEngine(cache_root=tmp_path / "cache", seed=42, max_inputs_per_callable=30)
    report = engine.run("statepkg", str(v1_dir), str(v2_dir))

    # 1. ConfigBox() should be filtered by ObjectNoiseFilter (sentinel + backward-compatible attribute addition)
    config_drifts = [d for d in report.behavioral_drifts if d.qualname == "ConfigBox"]
    assert len(config_drifts) == 0, f"Expected 0 drifts on ConfigBox, got: {config_drifts}"
    assert report.filtered_noise_count >= 1

    # 2. TokenBuffer.<stateful_chain> or TokenBuffer.compact should be caught!
    buffer_drifts = [d for d in report.behavioral_drifts if "TokenBuffer" in d.qualname]
    assert len(buffer_drifts) >= 1
    assert any(
        d.category in (DriftCategory.INPUT_MUTATION_DRIFT, DriftCategory.RETURN_VALUE_DRIFT)
        for d in buffer_drifts
    )

    # 3. Verify generated pytest file is 100% standalone (zero verdiff imports)
    paths = ReportGenerator.write_all(report, output_dir=tmp_path / "reports", prefix="statepkg")
    repro_code = paths["pytest"].read_text(encoding="utf-8")
    assert "from verdiff" not in repro_code
    assert "import verdiff" not in repro_code

    res = subprocess.run(
        [sys.executable, "-m", "pytest", str(paths["pytest"]), "-q"],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"Standalone repro failed:\n{res.stdout}\n{res.stderr}"
