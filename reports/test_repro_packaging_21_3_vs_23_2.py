r"""Auto-generated VerDiff pytest reproduction suite for packaging (21.3 vs 23.2)."""

from __future__ import annotations

import datetime
import decimal
import pathlib
import re
import uuid
import pytest

from verdiff.env_manager import IsolatedEnvManager
from verdiff.models import CallableContract, SynthesizedInput

PACKAGE = 'packaging'
VERSION_V1 = '21.3'
VERSION_V2 = '23.2'
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

def test_repro_01_packaging_specifiers_specifier_return_value_drift(dual_workers):
    """Reproduce return_value_drift (value_or_type_mismatch) on packaging.specifiers.Specifier."""
    w1, w2 = dual_workers
    contract = CallableContract(
        qualname='Specifier',
        module='packaging.specifiers',
        callable_kind='class',
    )
    minimal_input = SynthesizedInput(
        input_id='in_014_b4e16d',
        args=['===1.'],
        kwargs={},
        instance_args=[],
        instance_kwargs={},
    )
    out_v1 = w1.execute_callable(contract, minimal_input)
    out_v2 = w2.execute_callable(contract, minimal_input)
    assert out_v1.status == 'ok' and out_v2.status == 'ok'
    assert out_v1.return_canonical != out_v2.return_canonical

def test_repro_02_packaging_specifiers_specifierset_return_value_drift(dual_workers):
    """Reproduce return_value_drift (value_or_type_mismatch) on packaging.specifiers.SpecifierSet."""
    w1, w2 = dual_workers
    contract = CallableContract(
        qualname='SpecifierSet',
        module='packaging.specifiers',
        callable_kind='class',
    )
    minimal_input = SynthesizedInput(
        input_id='in_014_b4e16d',
        args=['===1.'],
        kwargs={},
        instance_args=[],
        instance_kwargs={},
    )
    out_v1 = w1.execute_callable(contract, minimal_input)
    out_v2 = w2.execute_callable(contract, minimal_input)
    assert out_v1.status == 'ok' and out_v2.status == 'ok'
    assert out_v1.return_canonical != out_v2.return_canonical

def test_repro_03_packaging_specifiers_specifierset_contains_exception_type_drift(dual_workers):
    """Reproduce exception_type_drift (pass_to_fail) on packaging.specifiers.SpecifierSet.contains."""
    w1, w2 = dual_workers
    contract = CallableContract(
        qualname='SpecifierSet.contains',
        module='packaging.specifiers',
        callable_kind='method',
    )
    minimal_input = SynthesizedInput(
        input_id='in_001_aeb9c8',
        args=[''],
        kwargs={},
        instance_args=[],
        instance_kwargs={},
    )
    out_v1 = w1.execute_callable(contract, minimal_input)
    out_v2 = w2.execute_callable(contract, minimal_input)
    assert out_v1.status == 'ok'
    assert out_v2.status == 'exception'
    assert out_v2.exception_type == 'InvalidVersion'

def test_repro_04_packaging_specifiers_specifierset_filter_return_value_drift(dual_workers):
    """Reproduce return_value_drift (value_or_type_mismatch) on packaging.specifiers.SpecifierSet.filter."""
    w1, w2 = dual_workers
    contract = CallableContract(
        qualname='SpecifierSet.filter',
        module='packaging.specifiers',
        callable_kind='method',
    )
    minimal_input = SynthesizedInput(
        input_id='in_001_332a4f',
        args=[[]],
        kwargs={},
        instance_args=[],
        instance_kwargs={},
    )
    out_v1 = w1.execute_callable(contract, minimal_input)
    out_v2 = w2.execute_callable(contract, minimal_input)
    assert out_v1.status == 'ok' and out_v2.status == 'ok'
    assert out_v1.return_canonical != out_v2.return_canonical

def test_repro_05_packaging_specifiers_specifierset_filter_exception_type_drift(dual_workers):
    """Reproduce exception_type_drift (pass_to_fail) on packaging.specifiers.SpecifierSet.filter."""
    w1, w2 = dual_workers
    contract = CallableContract(
        qualname='SpecifierSet.filter',
        module='packaging.specifiers',
        callable_kind='method',
    )
    minimal_input = SynthesizedInput(
        input_id='in_003_a58213',
        args=[['']],
        kwargs={},
        instance_args=[],
        instance_kwargs={},
    )
    out_v1 = w1.execute_callable(contract, minimal_input)
    out_v2 = w2.execute_callable(contract, minimal_input)
    assert out_v1.status == 'ok'
    assert out_v2.status == 'exception'
    assert out_v2.exception_type == 'InvalidVersion'

def test_repro_06_packaging_version_parse_exception_type_drift(dual_workers):
    """Reproduce exception_type_drift (pass_to_fail) on packaging.version.parse."""
    w1, w2 = dual_workers
    contract = CallableContract(
        qualname='parse',
        module='packaging.version',
        callable_kind='function',
    )
    minimal_input = SynthesizedInput(
        input_id='in_011_13c1c7',
        args=[''],
        kwargs={},
        instance_args=[],
        instance_kwargs={},
    )
    out_v1 = w1.execute_callable(contract, minimal_input)
    out_v2 = w2.execute_callable(contract, minimal_input)
    assert out_v1.status == 'ok'
    assert out_v2.status == 'exception'
    assert out_v2.exception_type == 'InvalidVersion'
