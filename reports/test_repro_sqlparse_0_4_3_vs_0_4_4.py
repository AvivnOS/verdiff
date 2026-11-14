r"""Standalone pytest regression suite for sqlparse (0.4.3 -> 0.4.4).

Zero third-party fuzzing dependencies required: uses only Python stdlib + pytest + target package.
"""

from __future__ import annotations

import copy
import datetime
import decimal
import importlib
import json
import os
import pathlib
import re
import statistics
import subprocess
import sys
import time
import uuid
from pathlib import Path
import pytest

PACKAGE = 'sqlparse'
VERSION_V1 = '0.4.3'
VERSION_V2 = '0.4.4'

_RUNNER_SNIPPET = r'''
import copy, datetime, decimal, importlib, inspect, json, os, pathlib, random, re, statistics, sys, time, uuid
payload = json.loads(sys.argv[1])
ns = {'datetime': datetime, 'decimal': decimal, 'pathlib': pathlib, 're': re, 'uuid': uuid}
mod = importlib.import_module(payload['module'])
qual = payload['qualname']
kind = payload['callable_kind']
args = eval(payload['args_expr'], ns)
kwargs = eval(payload['kwargs_expr'], ns)
inst_args = eval(payload['inst_args_expr'], ns)
inst_kwargs = eval(payload['inst_kwargs_expr'], ns)
chain = eval(payload['chain_expr'], ns)
def _safe_repr(o, limit=160):
    try:
        return re.sub(r' at 0x[0-9a-fA-F]+>', ' at 0xADDR>', repr(o))[:limit]
    except Exception as e:
        return f'<repr_error:{type(e).__name__}>'
def _snap_obj(o, depth=0):
    if depth > 2 or o is None or isinstance(o, (int, float, bool, str, bytes)):
        return _safe_repr(o, 160)
    if isinstance(o, (list, tuple, set, frozenset)):
        return [_snap_obj(x, depth + 1) for x in list(o)[:32]]
    d = {'__repr__': _safe_repr(o, 160)}
    for attr in sorted(dir(o)):
        if not attr.startswith('_'):
            try:
                val = getattr(o, attr)
                if not callable(val):
                    d[attr] = _snap_obj(val, depth + 1)
            except Exception as e:
                d[attr] = f'<exc:{type(e).__name__}>'
    if hasattr(o, '__iter__') and not isinstance(o, (str, bytes, bytearray)):
        try:
            d['__iter__'] = [repr(x)[:80] for x in list(o)[:32]]
        except Exception:
            pass
    return d
args_before = repr(args)
kwargs_before = repr(kwargs)
def _call_once():
    random.seed(42)
    os.urandom = random.Random(42).randbytes
    a_c = copy.deepcopy(args)
    k_c = copy.deepcopy(kwargs)
    ch_c = copy.deepcopy(chain)
    inst = None
    inst_before = None
    t0 = time.perf_counter_ns()
    try:
        if kind == 'stateful_chain':
            cls_name = qual.split('.')[0]
            cls_obj = getattr(mod, cls_name)
            inst = cls_obj(*copy.deepcopy(inst_args), **copy.deepcopy(inst_kwargs))
            inst_before = _snap_obj(inst)
            res = [getattr(inst, m)(*ma, **mk) for m, ma, mk in ch_c]
        elif '.' in qual:
            cls_name, m_name = qual.split('.', 1)
            cls_obj = getattr(mod, cls_name)
            raw_desc = inspect.getattr_static(cls_obj, m_name, None)
            if isinstance(raw_desc, (staticmethod, classmethod)):
                res = getattr(cls_obj, m_name)(*a_c, **k_c)
            else:
                inst = cls_obj(*copy.deepcopy(inst_args), **copy.deepcopy(inst_kwargs))
                inst_before = _snap_obj(inst)
                res = getattr(inst, m_name)(*a_c, **k_c)
        else:
            res = getattr(mod, qual)(*a_c, **k_c)
        if inspect.isgenerator(res) or type(res).__name__ in ('map', 'filter', 'zip', 'enumerate', 'reversed'):
            res = list(res)[:64]
        dt = (time.perf_counter_ns() - t0) / 1_000_000.0
        inst_after = _snap_obj(inst) if inst is not None else None
        state_probe = _snap_obj(res)
        return {'status': 'ok', 'type': f'{type(res).__module__}.{type(res).__qualname__}', 'repr': _safe_repr(res, 300), 'state': state_probe, 'after_args': _safe_repr(a_c, 300), 'after_inst': inst_after, 'ms': dt}
    except BaseException as exc:
        dt = (time.perf_counter_ns() - t0) / 1_000_000.0
        return {'status': 'exception', 'exc_type': type(exc).__qualname__, 'exc_msg': str(exc)[:300], 'ms': dt}
out = _call_once()
if payload.get('benchmark') and out['status'] == 'ok':
    samples = [_call_once()['ms'] for _ in range(5)]
    out['median_ms'] = statistics.median(samples)
print(json.dumps(out))
'''


def _find_env_python(pkg: str, ver: str) -> tuple[str, str | None]:
    local_p = Path(ver)
    if local_p.exists() and local_p.is_dir():
        return sys.executable, str(local_p.resolve())
    cache_envs = Path(__file__).resolve().parents[1] / '.cache' / 'envs'
    slug_prefix = re.sub(r'[^a-zA-Z0-9._-]+', '_', f'{pkg}_{ver}_py')
    if cache_envs.is_dir():
        for child in cache_envs.iterdir():
            if child.name.startswith(slug_prefix):
                py = child / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
                if py.is_file():
                    return str(py), None
    return sys.executable, None


def _invoke_standalone(version_spec: str, payload: dict) -> dict:
    py_exe, extra_path = _find_env_python(PACKAGE, version_spec)
    env = os.environ.copy()
    env['PYTHONHASHSEED'] = '0'
    if extra_path:
        env['PYTHONPATH'] = extra_path + os.pathsep + env.get('PYTHONPATH', '')
    proc = subprocess.run(
        [py_exe, '-c', _RUNNER_SNIPPET, json.dumps(payload)],
        capture_output=True, text=True, env=env, timeout=15.0
    )
    assert proc.returncode == 0, f'Subprocess failed: {proc.stderr}'
    lines = [ln for ln in proc.stdout.strip().splitlines() if ln.startswith('{')]
    return json.loads(lines[-1])

def test_repro_01_sqlparse_lexer_lexer_get_tokens_exception_type_drift():
    """Reproduce exception_type_drift (pass_to_fail) on sqlparse.lexer.Lexer.get_tokens.
    Minimal Call: Lexer.get_tokens('<')
    """
    payload = {
        'module': 'sqlparse.lexer',
        'qualname': 'Lexer.get_tokens',
        'callable_kind': 'staticmethod',
        'args_expr': "['<']",
        'kwargs_expr': '{}',
        'inst_args_expr': '[]',
        'inst_kwargs_expr': '{}',
        'chain_expr': '[]',
        'benchmark': False,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'ok'
    assert out_v2['status'] == 'exception'
    assert out_v2['exc_type'] == 'AttributeError'

def test_repro_02_sqlparse_lexer_tokenize_latency_regression():
    """Reproduce latency_regression (124.0x_latency_shift) on sqlparse.lexer.tokenize.
    Minimal Call: tokenize("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\")
    """
    payload = {
        'module': 'sqlparse.lexer',
        'qualname': 'tokenize',
        'callable_kind': 'function',
        'args_expr': '["\'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\"]',
        'kwargs_expr': '{}',
        'inst_args_expr': '[]',
        'inst_kwargs_expr': '{}',
        'chain_expr': '[]',
        'benchmark': True,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'ok' and out_v2['status'] == 'ok'
    m1, m2 = out_v1['median_ms'], out_v2['median_ms']
    assert max(m1, m2) >= min(max(m1, 0.05), max(m2, 0.05)) * 2.0

def test_repro_03_sqlparse_lexer_tokenize_latency_regression():
    """Reproduce latency_regression (120.7x_latency_shift) on sqlparse.lexer.tokenize.
    Minimal Call: tokenize("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", None)
    """
    payload = {
        'module': 'sqlparse.lexer',
        'qualname': 'tokenize',
        'callable_kind': 'function',
        'args_expr': '["\'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", None]',
        'kwargs_expr': '{}',
        'inst_args_expr': '[]',
        'inst_kwargs_expr': '{}',
        'chain_expr': '[]',
        'benchmark': True,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'ok' and out_v2['status'] == 'ok'
    m1, m2 = out_v1['median_ms'], out_v2['median_ms']
    assert max(m1, m2) >= min(max(m1, 0.05), max(m2, 0.05)) * 2.0

def test_repro_04_sqlparse_lexer_tokenize_return_value_drift():
    """Reproduce return_value_drift (value_or_type_mismatch) on sqlparse.lexer.tokenize.
    Minimal Call: tokenize('IN')
    """
    payload = {
        'module': 'sqlparse.lexer',
        'qualname': 'tokenize',
        'callable_kind': 'function',
        'args_expr': "['IN']",
        'kwargs_expr': '{}',
        'inst_args_expr': '[]',
        'inst_kwargs_expr': '{}',
        'chain_expr': '[]',
        'benchmark': False,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'ok' and out_v2['status'] == 'ok'
    assert (out_v1['type'], out_v1['repr'], out_v1['state']) != (out_v2['type'], out_v2['repr'], out_v2['state'])

def test_repro_05_sqlparse_lexer_tokenize_latency_regression():
    """Reproduce latency_regression (123.6x_latency_shift) on sqlparse.lexer.tokenize.
    Minimal Call: tokenize("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", ' ')
    """
    payload = {
        'module': 'sqlparse.lexer',
        'qualname': 'tokenize',
        'callable_kind': 'function',
        'args_expr': '["\'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", \' \']',
        'kwargs_expr': '{}',
        'inst_args_expr': '[]',
        'inst_kwargs_expr': '{}',
        'chain_expr': '[]',
        'benchmark': True,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'ok' and out_v2['status'] == 'ok'
    m1, m2 = out_v1['median_ms'], out_v2['median_ms']
    assert max(m1, m2) >= min(max(m1, 0.05), max(m2, 0.05)) * 2.0

def test_repro_06_sqlparse_engine_filter_stack_filterstack_stateful_chain__return_value_drift():
    """Reproduce return_value_drift (value_or_type_mismatch) on sqlparse.engine.filter_stack.FilterStack.<stateful_chain>.
    Minimal Call: obj = FilterStack(); obj.run('RE a IN (1);')
    """
    payload = {
        'module': 'sqlparse.engine.filter_stack',
        'qualname': 'FilterStack.<stateful_chain>',
        'callable_kind': 'stateful_chain',
        'args_expr': '[]',
        'kwargs_expr': '{}',
        'inst_args_expr': '[]',
        'inst_kwargs_expr': '{}',
        'chain_expr': "[('run', ['RE a IN (1);'], {})]",
        'benchmark': False,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'ok' and out_v2['status'] == 'ok'
    assert (out_v1['type'], out_v1['repr'], out_v1['state']) != (out_v2['type'], out_v2['repr'], out_v2['state'])

def test_repro_07_sqlparse_format_latency_regression():
    """Reproduce latency_regression (114.0x_latency_shift) on sqlparse.format.
    Minimal Call: format("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\")
    """
    payload = {
        'module': 'sqlparse',
        'qualname': 'format',
        'callable_kind': 'function',
        'args_expr': '["\'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\"]',
        'kwargs_expr': '{}',
        'inst_args_expr': '[]',
        'inst_kwargs_expr': '{}',
        'chain_expr': '[]',
        'benchmark': True,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'ok' and out_v2['status'] == 'ok'
    m1, m2 = out_v1['median_ms'], out_v2['median_ms']
    assert max(m1, m2) >= min(max(m1, 0.05), max(m2, 0.05)) * 2.0

def test_repro_08_sqlparse_format_latency_regression():
    """Reproduce latency_regression (111.0x_latency_shift) on sqlparse.format.
    Minimal Call: format("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", None)
    """
    payload = {
        'module': 'sqlparse',
        'qualname': 'format',
        'callable_kind': 'function',
        'args_expr': '["\'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", None]',
        'kwargs_expr': '{}',
        'inst_args_expr': '[]',
        'inst_kwargs_expr': '{}',
        'chain_expr': '[]',
        'benchmark': True,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'ok' and out_v2['status'] == 'ok'
    m1, m2 = out_v1['median_ms'], out_v2['median_ms']
    assert max(m1, m2) >= min(max(m1, 0.05), max(m2, 0.05)) * 2.0

def test_repro_09_sqlparse_format_latency_regression():
    """Reproduce latency_regression (115.7x_latency_shift) on sqlparse.format.
    Minimal Call: format("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", '')
    """
    payload = {
        'module': 'sqlparse',
        'qualname': 'format',
        'callable_kind': 'function',
        'args_expr': '["\'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", \'\']',
        'kwargs_expr': '{}',
        'inst_args_expr': '[]',
        'inst_kwargs_expr': '{}',
        'chain_expr': '[]',
        'benchmark': True,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'ok' and out_v2['status'] == 'ok'
    m1, m2 = out_v1['median_ms'], out_v2['median_ms']
    assert max(m1, m2) >= min(max(m1, 0.05), max(m2, 0.05)) * 2.0

def test_repro_10_sqlparse_format_latency_regression():
    """Reproduce latency_regression (109.7x_latency_shift) on sqlparse.format.
    Minimal Call: format("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", '_diff')
    """
    payload = {
        'module': 'sqlparse',
        'qualname': 'format',
        'callable_kind': 'function',
        'args_expr': '["\'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", \'_diff\']',
        'kwargs_expr': '{}',
        'inst_args_expr': '[]',
        'inst_kwargs_expr': '{}',
        'chain_expr': '[]',
        'benchmark': True,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'ok' and out_v2['status'] == 'ok'
    m1, m2 = out_v1['median_ms'], out_v2['median_ms']
    assert max(m1, m2) >= min(max(m1, 0.05), max(m2, 0.05)) * 2.0

def test_repro_11_sqlparse_format_latency_regression():
    """Reproduce latency_regression (111.4x_latency_shift) on sqlparse.format.
    Minimal Call: format("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", ' ')
    """
    payload = {
        'module': 'sqlparse',
        'qualname': 'format',
        'callable_kind': 'function',
        'args_expr': '["\'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", \' \']',
        'kwargs_expr': '{}',
        'inst_args_expr': '[]',
        'inst_kwargs_expr': '{}',
        'chain_expr': '[]',
        'benchmark': True,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'ok' and out_v2['status'] == 'ok'
    m1, m2 = out_v1['median_ms'], out_v2['median_ms']
    assert max(m1, m2) >= min(max(m1, 0.05), max(m2, 0.05)) * 2.0

def test_repro_12_sqlparse_parse_latency_regression():
    """Reproduce latency_regression (46.0x_latency_shift) on sqlparse.parse.
    Minimal Call: parse("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\")
    """
    payload = {
        'module': 'sqlparse',
        'qualname': 'parse',
        'callable_kind': 'function',
        'args_expr': '["\'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\"]',
        'kwargs_expr': '{}',
        'inst_args_expr': '[]',
        'inst_kwargs_expr': '{}',
        'chain_expr': '[]',
        'benchmark': True,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'ok' and out_v2['status'] == 'ok'
    m1, m2 = out_v1['median_ms'], out_v2['median_ms']
    assert max(m1, m2) >= min(max(m1, 0.05), max(m2, 0.05)) * 2.0

def test_repro_13_sqlparse_parse_latency_regression():
    """Reproduce latency_regression (48.4x_latency_shift) on sqlparse.parse.
    Minimal Call: parse("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", None)
    """
    payload = {
        'module': 'sqlparse',
        'qualname': 'parse',
        'callable_kind': 'function',
        'args_expr': '["\'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", None]',
        'kwargs_expr': '{}',
        'inst_args_expr': '[]',
        'inst_kwargs_expr': '{}',
        'chain_expr': '[]',
        'benchmark': True,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'ok' and out_v2['status'] == 'ok'
    m1, m2 = out_v1['median_ms'], out_v2['median_ms']
    assert max(m1, m2) >= min(max(m1, 0.05), max(m2, 0.05)) * 2.0

def test_repro_14_sqlparse_parse_latency_regression():
    """Reproduce latency_regression (50.4x_latency_shift) on sqlparse.parse.
    Minimal Call: parse("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", '')
    """
    payload = {
        'module': 'sqlparse',
        'qualname': 'parse',
        'callable_kind': 'function',
        'args_expr': '["\'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", \'\']',
        'kwargs_expr': '{}',
        'inst_args_expr': '[]',
        'inst_kwargs_expr': '{}',
        'chain_expr': '[]',
        'benchmark': True,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'ok' and out_v2['status'] == 'ok'
    m1, m2 = out_v1['median_ms'], out_v2['median_ms']
    assert max(m1, m2) >= min(max(m1, 0.05), max(m2, 0.05)) * 2.0

def test_repro_15_sqlparse_parse_return_value_drift():
    """Reproduce return_value_drift (value_or_type_mismatch) on sqlparse.parse.
    Minimal Call: parse('IN')
    """
    payload = {
        'module': 'sqlparse',
        'qualname': 'parse',
        'callable_kind': 'function',
        'args_expr': "['IN']",
        'kwargs_expr': '{}',
        'inst_args_expr': '[]',
        'inst_kwargs_expr': '{}',
        'chain_expr': '[]',
        'benchmark': False,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'ok' and out_v2['status'] == 'ok'
    assert (out_v1['type'], out_v1['repr'], out_v1['state']) != (out_v2['type'], out_v2['repr'], out_v2['state'])

def test_repro_16_sqlparse_parse_latency_regression():
    """Reproduce latency_regression (50.2x_latency_shift) on sqlparse.parse.
    Minimal Call: parse("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", ' ')
    """
    payload = {
        'module': 'sqlparse',
        'qualname': 'parse',
        'callable_kind': 'function',
        'args_expr': '["\'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", \' \']',
        'kwargs_expr': '{}',
        'inst_args_expr': '[]',
        'inst_kwargs_expr': '{}',
        'chain_expr': '[]',
        'benchmark': True,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'ok' and out_v2['status'] == 'ok'
    m1, m2 = out_v1['median_ms'], out_v2['median_ms']
    assert max(m1, m2) >= min(max(m1, 0.05), max(m2, 0.05)) * 2.0

def test_repro_17_sqlparse_parsestream_latency_regression():
    """Reproduce latency_regression (65.2x_latency_shift) on sqlparse.parsestream.
    Minimal Call: parsestream("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\")
    """
    payload = {
        'module': 'sqlparse',
        'qualname': 'parsestream',
        'callable_kind': 'function',
        'args_expr': '["\'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\"]',
        'kwargs_expr': '{}',
        'inst_args_expr': '[]',
        'inst_kwargs_expr': '{}',
        'chain_expr': '[]',
        'benchmark': True,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'ok' and out_v2['status'] == 'ok'
    m1, m2 = out_v1['median_ms'], out_v2['median_ms']
    assert max(m1, m2) >= min(max(m1, 0.05), max(m2, 0.05)) * 2.0

def test_repro_18_sqlparse_split_latency_regression():
    """Reproduce latency_regression (141.6x_latency_shift) on sqlparse.split.
    Minimal Call: split("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\")
    """
    payload = {
        'module': 'sqlparse',
        'qualname': 'split',
        'callable_kind': 'function',
        'args_expr': '["\'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\"]',
        'kwargs_expr': '{}',
        'inst_args_expr': '[]',
        'inst_kwargs_expr': '{}',
        'chain_expr': '[]',
        'benchmark': True,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'ok' and out_v2['status'] == 'ok'
    m1, m2 = out_v1['median_ms'], out_v2['median_ms']
    assert max(m1, m2) >= min(max(m1, 0.05), max(m2, 0.05)) * 2.0

def test_repro_19_sqlparse_split_latency_regression():
    """Reproduce latency_regression (149.2x_latency_shift) on sqlparse.split.
    Minimal Call: split("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", None)
    """
    payload = {
        'module': 'sqlparse',
        'qualname': 'split',
        'callable_kind': 'function',
        'args_expr': '["\'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", None]',
        'kwargs_expr': '{}',
        'inst_args_expr': '[]',
        'inst_kwargs_expr': '{}',
        'chain_expr': '[]',
        'benchmark': True,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'ok' and out_v2['status'] == 'ok'
    m1, m2 = out_v1['median_ms'], out_v2['median_ms']
    assert max(m1, m2) >= min(max(m1, 0.05), max(m2, 0.05)) * 2.0

def test_repro_20_sqlparse_split_latency_regression():
    """Reproduce latency_regression (150.6x_latency_shift) on sqlparse.split.
    Minimal Call: split("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", '')
    """
    payload = {
        'module': 'sqlparse',
        'qualname': 'split',
        'callable_kind': 'function',
        'args_expr': '["\'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", \'\']',
        'kwargs_expr': '{}',
        'inst_args_expr': '[]',
        'inst_kwargs_expr': '{}',
        'chain_expr': '[]',
        'benchmark': True,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'ok' and out_v2['status'] == 'ok'
    m1, m2 = out_v1['median_ms'], out_v2['median_ms']
    assert max(m1, m2) >= min(max(m1, 0.05), max(m2, 0.05)) * 2.0

def test_repro_21_sqlparse_split_latency_regression():
    """Reproduce latency_regression (139.0x_latency_shift) on sqlparse.split.
    Minimal Call: split("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", ' ')
    """
    payload = {
        'module': 'sqlparse',
        'qualname': 'split',
        'callable_kind': 'function',
        'args_expr': '["\'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", \' \']',
        'kwargs_expr': '{}',
        'inst_args_expr': '[]',
        'inst_kwargs_expr': '{}',
        'chain_expr': '[]',
        'benchmark': True,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'ok' and out_v2['status'] == 'ok'
    m1, m2 = out_v1['median_ms'], out_v2['median_ms']
    assert max(m1, m2) >= min(max(m1, 0.05), max(m2, 0.05)) * 2.0

def test_repro_22_sqlparse_split_latency_regression():
    """Reproduce latency_regression (154.0x_latency_shift) on sqlparse.split.
    Minimal Call: split("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", '\t\r\n')
    """
    payload = {
        'module': 'sqlparse',
        'qualname': 'split',
        'callable_kind': 'function',
        'args_expr': '["\'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", \'\\t\\r\\n\']',
        'kwargs_expr': '{}',
        'inst_args_expr': '[]',
        'inst_kwargs_expr': '{}',
        'chain_expr': '[]',
        'benchmark': True,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'ok' and out_v2['status'] == 'ok'
    m1, m2 = out_v1['median_ms'], out_v2['median_ms']
    assert max(m1, m2) >= min(max(m1, 0.05), max(m2, 0.05)) * 2.0
