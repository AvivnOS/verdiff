r"""Auto-generated VerDiff pytest reproduction suite for semver (2.13.0 vs 3.0.2)."""

from __future__ import annotations

import datetime
import decimal
import pathlib
import re
import uuid
import pytest

from verdiff.env_manager import IsolatedEnvManager
from verdiff.models import CallableContract, SynthesizedInput

PACKAGE = 'semver'
VERSION_V1 = '2.13.0'
VERSION_V2 = '3.0.2'
PYTHON_SPEC = '3.12.14'


@pytest.fixture(scope='module')
def dual_workers():
    mgr = IsolatedEnvManager()
    w1 = mgr.ensure_environment(PACKAGE, VERSION_V1)
    w2 = mgr.ensure_environment(PACKAGE, VERSION_V2)
    try:
        yield w1, w2
    finally:
        w1.close()
        w2.close()

def test_repro_01_semver_bump_build_return_value_drift(dual_workers):
    """Reproduce return_value_drift (value_or_type_mismatch) on semver.bump_build."""
    w1, w2 = dual_workers
    contract = CallableContract(
        qualname='bump_build',
        module='semver',
        callable_kind='function',
    )
    minimal_input = SynthesizedInput(
        input_id='in_004_c6f6a9',
        args=['1.0.0', ''],
        kwargs={},
        instance_args=[],
        instance_kwargs={},
    )
    out_v1 = w1.execute_callable(contract, minimal_input)
    out_v2 = w2.execute_callable(contract, minimal_input)
    assert out_v1.status == 'ok' and out_v2.status == 'ok'
    assert out_v1.return_canonical != out_v2.return_canonical

def test_repro_02_semver_bump_build_exception_type_drift(dual_workers):
    """Reproduce exception_type_drift (fail_to_pass) on semver.bump_build."""
    w1, w2 = dual_workers
    contract = CallableContract(
        qualname='bump_build',
        module='semver',
        callable_kind='function',
    )
    minimal_input = SynthesizedInput(
        input_id='in_022_409d8e',
        args=['1.0.0', b'b'],
        kwargs={},
        instance_args=[],
        instance_kwargs={},
    )
    out_v1 = w1.execute_callable(contract, minimal_input)
    out_v2 = w2.execute_callable(contract, minimal_input)
    assert out_v1.status == 'exception'
    assert out_v2.status == 'ok'
    assert out_v1.exception_type == 'TypeError'

def test_repro_03_semver_bump_prerelease_return_value_drift(dual_workers):
    """Reproduce return_value_drift (value_or_type_mismatch) on semver.bump_prerelease."""
    w1, w2 = dual_workers
    contract = CallableContract(
        qualname='bump_prerelease',
        module='semver',
        callable_kind='function',
    )
    minimal_input = SynthesizedInput(
        input_id='in_004_c6f6a9',
        args=['1.0.0', ''],
        kwargs={},
        instance_args=[],
        instance_kwargs={},
    )
    out_v1 = w1.execute_callable(contract, minimal_input)
    out_v2 = w2.execute_callable(contract, minimal_input)
    assert out_v1.status == 'ok' and out_v2.status == 'ok'
    assert out_v1.return_canonical != out_v2.return_canonical

def test_repro_04_semver_bump_prerelease_exception_type_drift(dual_workers):
    """Reproduce exception_type_drift (fail_to_pass) on semver.bump_prerelease."""
    w1, w2 = dual_workers
    contract = CallableContract(
        qualname='bump_prerelease',
        module='semver',
        callable_kind='function',
    )
    minimal_input = SynthesizedInput(
        input_id='in_022_409d8e',
        args=['1.0.0', b'b'],
        kwargs={},
        instance_args=[],
        instance_kwargs={},
    )
    out_v1 = w1.execute_callable(contract, minimal_input)
    out_v2 = w2.execute_callable(contract, minimal_input)
    assert out_v1.status == 'exception'
    assert out_v2.status == 'ok'
    assert out_v1.exception_type == 'TypeError'

def test_repro_05_semver_parse_return_value_drift(dual_workers):
    """Reproduce return_value_drift (value_or_type_mismatch) on semver.parse."""
    w1, w2 = dual_workers
    contract = CallableContract(
        qualname='parse',
        module='semver',
        callable_kind='function',
    )
    minimal_input = SynthesizedInput(
        input_id='in_001_675c5d',
        args=['1.0.0'],
        kwargs={},
        instance_args=[],
        instance_kwargs={},
    )
    out_v1 = w1.execute_callable(contract, minimal_input)
    out_v2 = w2.execute_callable(contract, minimal_input)
    assert out_v1.status == 'ok' and out_v2.status == 'ok'
    assert out_v1.return_canonical != out_v2.return_canonical

def test_repro_06_semver_parse_version_info_return_value_drift(dual_workers):
    """Reproduce return_value_drift (value_or_type_mismatch) on semver.parse_version_info."""
    w1, w2 = dual_workers
    contract = CallableContract(
        qualname='parse_version_info',
        module='semver',
        callable_kind='function',
    )
    minimal_input = SynthesizedInput(
        input_id='in_001_675c5d',
        args=['1.0.0'],
        kwargs={},
        instance_args=[],
        instance_kwargs={},
    )
    out_v1 = w1.execute_callable(contract, minimal_input)
    out_v2 = w2.execute_callable(contract, minimal_input)
    assert out_v1.status == 'ok' and out_v2.status == 'ok'
    assert out_v1.return_canonical != out_v2.return_canonical
