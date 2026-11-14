r"""Standalone pytest regression suite for urllib3 (1.26.18 -> 2.0.7).

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

PACKAGE = 'urllib3'
VERSION_V1 = '1.26.18'
VERSION_V2 = '2.0.7'

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

def test_repro_01_urllib3_connection_httpheaderdict_exception_type_drift():
    """Reproduce exception_type_drift (fail_to_pass) on urllib3.connection.HTTPHeaderDict.
    Minimal Call: HTTPHeaderDict(0.0)
    """
    payload = {
        'module': 'urllib3.connection',
        'qualname': 'HTTPHeaderDict',
        'callable_kind': 'class',
        'args_expr': '[0.0]',
        'kwargs_expr': '{}',
        'inst_args_expr': '[]',
        'inst_kwargs_expr': '{}',
        'chain_expr': '[]',
        'benchmark': False,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'exception'
    assert out_v2['status'] == 'ok'
    assert out_v1['exc_type'] == 'TypeError'

def test_repro_02_urllib3_connection_httpheaderdict_stateful_chain__input_mutation_drift():
    """Reproduce input_mutation_drift (in_place_mutation) on urllib3.connection.HTTPHeaderDict.<stateful_chain>.
    Minimal Call: obj = HTTPHeaderDict(); obj.add(b'', '')
    """
    payload = {
        'module': 'urllib3.connection',
        'qualname': 'HTTPHeaderDict.<stateful_chain>',
        'callable_kind': 'stateful_chain',
        'args_expr': '[]',
        'kwargs_expr': '{}',
        'inst_args_expr': '[]',
        'inst_kwargs_expr': '{}',
        'chain_expr': "[('add', [b'', ''], {})]",
        'benchmark': False,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'ok' and out_v2['status'] == 'ok'
    assert (out_v1['after_args'], out_v1['after_inst']) != (out_v2['after_args'], out_v2['after_inst'])

def test_repro_03_urllib3_connection_httpheaderdict_extend_exception_type_drift():
    """Reproduce exception_type_drift (fail_to_pass) on urllib3.connection.HTTPHeaderDict.extend.
    Minimal Call: HTTPHeaderDict.extend(0)
    """
    payload = {
        'module': 'urllib3.connection',
        'qualname': 'HTTPHeaderDict.extend',
        'callable_kind': 'method',
        'args_expr': '[0]',
        'kwargs_expr': '{}',
        'inst_args_expr': '[]',
        'inst_kwargs_expr': '{}',
        'chain_expr': '[]',
        'benchmark': False,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'exception'
    assert out_v2['status'] == 'ok'
    assert out_v1['exc_type'] == 'TypeError'

def test_repro_04_urllib3_connection_httpheaderdict_setdefault_input_mutation_drift():
    """Reproduce input_mutation_drift (in_place_mutation) on urllib3.connection.HTTPHeaderDict.setdefault.
    Minimal Call: HTTPHeaderDict.setdefault('')
    """
    payload = {
        'module': 'urllib3.connection',
        'qualname': 'HTTPHeaderDict.setdefault',
        'callable_kind': 'method',
        'args_expr': "['']",
        'kwargs_expr': '{}',
        'inst_args_expr': '[]',
        'inst_kwargs_expr': '{}',
        'chain_expr': '[]',
        'benchmark': False,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'ok' and out_v2['status'] == 'ok'
    assert (out_v1['after_args'], out_v1['after_inst']) != (out_v2['after_args'], out_v2['after_inst'])

def test_repro_05_urllib3_connectionpool_connectionpool_exception_type_drift():
    """Reproduce exception_type_drift (pass_to_fail) on urllib3.connectionpool.ConnectionPool.
    Minimal Call: ConnectionPool(b'a')
    """
    payload = {
        'module': 'urllib3.connectionpool',
        'qualname': 'ConnectionPool',
        'callable_kind': 'class',
        'args_expr': "[b'a']",
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
    assert out_v2['exc_type'] == 'TypeError'

def test_repro_06_urllib3_connectionpool_connection_from_url_return_value_drift():
    """Reproduce return_value_drift (value_or_type_mismatch) on urllib3.connectionpool.connection_from_url.
    Minimal Call: connection_from_url('h')
    """
    payload = {
        'module': 'urllib3.connectionpool',
        'qualname': 'connection_from_url',
        'callable_kind': 'function',
        'args_expr': "['h']",
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

def test_repro_07_urllib3_connectionpool_connection_from_url_return_value_drift():
    """Reproduce return_value_drift (value_or_type_mismatch) on urllib3.connectionpool.connection_from_url.
    Minimal Call: connection_from_url('e')
    """
    payload = {
        'module': 'urllib3.connectionpool',
        'qualname': 'connection_from_url',
        'callable_kind': 'function',
        'args_expr': "['e']",
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

def test_repro_08_urllib3_fields_requestfield_return_value_drift():
    """Reproduce return_value_drift (value_or_type_mismatch) on urllib3.fields.RequestField.
    Minimal Call: RequestField('', {}, None, None, None)
    """
    payload = {
        'module': 'urllib3.fields',
        'qualname': 'RequestField',
        'callable_kind': 'class',
        'args_expr': "['', {}, None, None, None]",
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

def test_repro_09_urllib3_fields_requestfield_stateful_chain__exception_type_drift():
    """Reproduce exception_type_drift (exception_class_changed) on urllib3.fields.RequestField.<stateful_chain>.
    Minimal Call: obj = RequestField(3, {}); obj.make_multipart()
    """
    payload = {
        'module': 'urllib3.fields',
        'qualname': 'RequestField.<stateful_chain>',
        'callable_kind': 'stateful_chain',
        'args_expr': '[]',
        'kwargs_expr': '{}',
        'inst_args_expr': '[3, {}]',
        'inst_kwargs_expr': '{}',
        'chain_expr': "[('make_multipart', [], {})]",
        'benchmark': False,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'exception'
    assert out_v2['status'] == 'exception'
    assert out_v1['exc_type'] == 'TypeError'
    assert out_v2['exc_type'] == 'AttributeError'

def test_repro_10_urllib3_fields_requestfield_from_tuples_exception_type_drift():
    """Reproduce exception_type_drift (exception_class_changed) on urllib3.fields.RequestField.from_tuples.
    Minimal Call: RequestField.from_tuples(0, 0)
    """
    payload = {
        'module': 'urllib3.fields',
        'qualname': 'RequestField.from_tuples',
        'callable_kind': 'classmethod',
        'args_expr': '[0, 0]',
        'kwargs_expr': '{}',
        'inst_args_expr': '[]',
        'inst_kwargs_expr': '{}',
        'chain_expr': '[]',
        'benchmark': False,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'exception'
    assert out_v2['status'] == 'exception'
    assert out_v1['exc_type'] == 'TypeError'
    assert out_v2['exc_type'] == 'AttributeError'

def test_repro_11_urllib3_fields_requestfield_from_tuples_return_value_drift():
    """Reproduce return_value_drift (value_or_type_mismatch) on urllib3.fields.RequestField.from_tuples.
    Minimal Call: RequestField.from_tuples('\t', 0)
    """
    payload = {
        'module': 'urllib3.fields',
        'qualname': 'RequestField.from_tuples',
        'callable_kind': 'classmethod',
        'args_expr': "['\\t', 0]",
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

def test_repro_12_urllib3_fields_requestfield_make_multipart_exception_type_drift():
    """Reproduce exception_type_drift (pass_to_fail) on urllib3.fields.RequestField.make_multipart.
    Minimal Call: RequestField('Content-Disposition', {}).make_multipart([0])
    """
    payload = {
        'module': 'urllib3.fields',
        'qualname': 'RequestField.make_multipart',
        'callable_kind': 'method',
        'args_expr': '[[0]]',
        'kwargs_expr': '{}',
        'inst_args_expr': "['Content-Disposition', {}]",
        'inst_kwargs_expr': '{}',
        'chain_expr': '[]',
        'benchmark': False,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'ok'
    assert out_v2['status'] == 'exception'
    assert out_v2['exc_type'] == 'TypeError'

def test_repro_13_urllib3_fields_format_header_param_exception_type_drift():
    """Reproduce exception_type_drift (exception_class_changed) on urllib3.fields.format_header_param.
    Minimal Call: format_header_param(0, 0)
    """
    payload = {
        'module': 'urllib3.fields',
        'qualname': 'format_header_param',
        'callable_kind': 'function',
        'args_expr': '[0, 0]',
        'kwargs_expr': '{}',
        'inst_args_expr': '[]',
        'inst_kwargs_expr': '{}',
        'chain_expr': '[]',
        'benchmark': False,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'exception'
    assert out_v2['status'] == 'exception'
    assert out_v1['exc_type'] == 'TypeError'
    assert out_v2['exc_type'] == 'AttributeError'

def test_repro_14_urllib3_fields_format_header_param_return_value_drift():
    """Reproduce return_value_drift (value_or_type_mismatch) on urllib3.fields.format_header_param.
    Minimal Call: format_header_param(0, '\t')
    """
    payload = {
        'module': 'urllib3.fields',
        'qualname': 'format_header_param',
        'callable_kind': 'function',
        'args_expr': "[0, '\\t']",
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

def test_repro_15_urllib3_fields_format_header_param_html5_exception_type_drift():
    """Reproduce exception_type_drift (exception_class_changed) on urllib3.fields.format_header_param_html5.
    Minimal Call: format_header_param_html5('', 0)
    """
    payload = {
        'module': 'urllib3.fields',
        'qualname': 'format_header_param_html5',
        'callable_kind': 'function',
        'args_expr': "['', 0]",
        'kwargs_expr': '{}',
        'inst_args_expr': '[]',
        'inst_kwargs_expr': '{}',
        'chain_expr': '[]',
        'benchmark': False,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'exception'
    assert out_v2['status'] == 'exception'
    assert out_v1['exc_type'] == 'TypeError'
    assert out_v2['exc_type'] == 'AttributeError'

def test_repro_16_urllib3_fields_format_header_param_html5_return_value_drift():
    """Reproduce return_value_drift (value_or_type_mismatch) on urllib3.fields.format_header_param_html5.
    Minimal Call: format_header_param_html5('', '\t')
    """
    payload = {
        'module': 'urllib3.fields',
        'qualname': 'format_header_param_html5',
        'callable_kind': 'function',
        'args_expr': "['', '\\t']",
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

def test_repro_17_urllib3_poolmanager_poolmanager_stateful_chain__return_value_drift():
    """Reproduce return_value_drift (value_or_type_mismatch) on urllib3.poolmanager.PoolManager.<stateful_chain>.
    Minimal Call: obj = PoolManager(); obj.connection_from_host('a')
    """
    payload = {
        'module': 'urllib3.poolmanager',
        'qualname': 'PoolManager.<stateful_chain>',
        'callable_kind': 'stateful_chain',
        'args_expr': '[]',
        'kwargs_expr': '{}',
        'inst_args_expr': '[]',
        'inst_kwargs_expr': '{}',
        'chain_expr': "[('connection_from_host', ['a'], {})]",
        'benchmark': False,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'ok' and out_v2['status'] == 'ok'
    assert (out_v1['type'], out_v1['repr'], out_v1['state']) != (out_v2['type'], out_v2['repr'], out_v2['state'])

def test_repro_18_urllib3_poolmanager_poolmanager_connection_from_host_return_value_drift():
    """Reproduce return_value_drift (value_or_type_mismatch) on urllib3.poolmanager.PoolManager.connection_from_host.
    Minimal Call: PoolManager.connection_from_host('h')
    """
    payload = {
        'module': 'urllib3.poolmanager',
        'qualname': 'PoolManager.connection_from_host',
        'callable_kind': 'method',
        'args_expr': "['h']",
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

def test_repro_19_urllib3_poolmanager_poolmanager_connection_from_url_return_value_drift():
    """Reproduce return_value_drift (value_or_type_mismatch) on urllib3.poolmanager.PoolManager.connection_from_url.
    Minimal Call: PoolManager.connection_from_url('h')
    """
    payload = {
        'module': 'urllib3.poolmanager',
        'qualname': 'PoolManager.connection_from_url',
        'callable_kind': 'method',
        'args_expr': "['h']",
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

def test_repro_20_urllib3_poolmanager_poolmanager_connection_from_url_return_value_drift():
    """Reproduce return_value_drift (value_or_type_mismatch) on urllib3.poolmanager.PoolManager.connection_from_url.
    Minimal Call: PoolManager.connection_from_url('e')
    """
    payload = {
        'module': 'urllib3.poolmanager',
        'qualname': 'PoolManager.connection_from_url',
        'callable_kind': 'method',
        'args_expr': "['e']",
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

def test_repro_21_urllib3_poolmanager_proxymanager_connection_from_host_return_value_drift():
    """Reproduce return_value_drift (value_or_type_mismatch) on urllib3.poolmanager.ProxyManager.connection_from_host.
    Minimal Call: ProxyManager('https://example.com/path?a=1&b=2#sec').connection_from_host('')
    """
    payload = {
        'module': 'urllib3.poolmanager',
        'qualname': 'ProxyManager.connection_from_host',
        'callable_kind': 'method',
        'args_expr': "['']",
        'kwargs_expr': '{}',
        'inst_args_expr': "['https://example.com/path?a=1&b=2#sec']",
        'inst_kwargs_expr': '{}',
        'chain_expr': '[]',
        'benchmark': False,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'ok' and out_v2['status'] == 'ok'
    assert (out_v1['type'], out_v1['repr'], out_v1['state']) != (out_v2['type'], out_v2['repr'], out_v2['state'])

def test_repro_22_urllib3_poolmanager_proxymanager_connection_from_host_return_value_drift():
    """Reproduce return_value_drift (value_or_type_mismatch) on urllib3.poolmanager.ProxyManager.connection_from_host.
    Minimal Call: ProxyManager('http://example.com:8080/test').connection_from_host('')
    """
    payload = {
        'module': 'urllib3.poolmanager',
        'qualname': 'ProxyManager.connection_from_host',
        'callable_kind': 'method',
        'args_expr': "['']",
        'kwargs_expr': '{}',
        'inst_args_expr': "['http://example.com:8080/test']",
        'inst_kwargs_expr': '{}',
        'chain_expr': '[]',
        'benchmark': False,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'ok' and out_v2['status'] == 'ok'
    assert (out_v1['type'], out_v1['repr'], out_v1['state']) != (out_v2['type'], out_v2['repr'], out_v2['state'])

def test_repro_23_urllib3_poolmanager_proxymanager_connection_from_url_return_value_drift():
    """Reproduce return_value_drift (value_or_type_mismatch) on urllib3.poolmanager.ProxyManager.connection_from_url.
    Minimal Call: ProxyManager('https://example.com/path?a=1&b=2#sec').connection_from_url('')
    """
    payload = {
        'module': 'urllib3.poolmanager',
        'qualname': 'ProxyManager.connection_from_url',
        'callable_kind': 'method',
        'args_expr': "['']",
        'kwargs_expr': '{}',
        'inst_args_expr': "['https://example.com/path?a=1&b=2#sec']",
        'inst_kwargs_expr': '{}',
        'chain_expr': '[]',
        'benchmark': False,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'ok' and out_v2['status'] == 'ok'
    assert (out_v1['type'], out_v1['repr'], out_v1['state']) != (out_v2['type'], out_v2['repr'], out_v2['state'])

def test_repro_24_urllib3_poolmanager_proxymanager_connection_from_url_return_value_drift():
    """Reproduce return_value_drift (value_or_type_mismatch) on urllib3.poolmanager.ProxyManager.connection_from_url.
    Minimal Call: ProxyManager('http://example.com:8080/test').connection_from_url('')
    """
    payload = {
        'module': 'urllib3.poolmanager',
        'qualname': 'ProxyManager.connection_from_url',
        'callable_kind': 'method',
        'args_expr': "['']",
        'kwargs_expr': '{}',
        'inst_args_expr': "['http://example.com:8080/test']",
        'inst_kwargs_expr': '{}',
        'chain_expr': '[]',
        'benchmark': False,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'ok' and out_v2['status'] == 'ok'
    assert (out_v1['type'], out_v1['repr'], out_v1['state']) != (out_v2['type'], out_v2['repr'], out_v2['state'])

def test_repro_25_urllib3_poolmanager_proxy_from_url_return_value_drift():
    """Reproduce return_value_drift (value_or_type_mismatch) on urllib3.poolmanager.proxy_from_url.
    Minimal Call: proxy_from_url('https:')
    """
    payload = {
        'module': 'urllib3.poolmanager',
        'qualname': 'proxy_from_url',
        'callable_kind': 'function',
        'args_expr': "['https:']",
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

def test_repro_26_urllib3_response_httpresponse_read_exception_type_drift():
    """Reproduce exception_type_drift (pass_to_fail) on urllib3.response.HTTPResponse.read.
    Minimal Call: HTTPResponse.read('')
    """
    payload = {
        'module': 'urllib3.response',
        'qualname': 'HTTPResponse.read',
        'callable_kind': 'method',
        'args_expr': "['']",
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
    assert out_v2['exc_type'] == 'TypeError'

def test_repro_27_urllib3_response_httpresponse_read_return_value_drift():
    """Reproduce return_value_drift (value_or_type_mismatch) on urllib3.response.HTTPResponse.read.
    Minimal Call: HTTPResponse.read(0)
    """
    payload = {
        'module': 'urllib3.response',
        'qualname': 'HTTPResponse.read',
        'callable_kind': 'method',
        'args_expr': '[0]',
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

def test_repro_28_urllib3_response_httpresponse_read_exception_type_drift():
    """Reproduce exception_type_drift (pass_to_fail) on urllib3.response.HTTPResponse.read.
    Minimal Call: HTTPResponse.read(-1)
    """
    payload = {
        'module': 'urllib3.response',
        'qualname': 'HTTPResponse.read',
        'callable_kind': 'method',
        'args_expr': '[-1]',
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
    assert out_v2['exc_type'] == 'RuntimeError'

def test_repro_29_urllib3_response_httpresponse_readinto_exception_type_drift():
    """Reproduce exception_type_drift (fail_to_pass) on urllib3.response.HTTPResponse.readinto.
    Minimal Call: HTTPResponse.readinto('')
    """
    payload = {
        'module': 'urllib3.response',
        'qualname': 'HTTPResponse.readinto',
        'callable_kind': 'method',
        'args_expr': "['']",
        'kwargs_expr': '{}',
        'inst_args_expr': '[]',
        'inst_kwargs_expr': '{}',
        'chain_expr': '[]',
        'benchmark': False,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'exception'
    assert out_v2['status'] == 'ok'
    assert out_v1['exc_type'] == 'TypeError'

def test_repro_30_urllib3_util_connection_is_connection_dropped_exception_type_drift():
    """Reproduce exception_type_drift (pass_to_fail) on urllib3.util.connection.is_connection_dropped.
    Minimal Call: is_connection_dropped('')
    """
    payload = {
        'module': 'urllib3.util.connection',
        'qualname': 'is_connection_dropped',
        'callable_kind': 'function',
        'args_expr': "['']",
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

def test_repro_31_urllib3_util_retry_retry_sleep_for_retry_exception_type_drift():
    """Reproduce exception_type_drift (exception_class_changed) on urllib3.util.retry.Retry.sleep_for_retry.
    Minimal Call: Retry.sleep_for_retry()
    """
    payload = {
        'module': 'urllib3.util.retry',
        'qualname': 'Retry.sleep_for_retry',
        'callable_kind': 'method',
        'args_expr': '[]',
        'kwargs_expr': '{}',
        'inst_args_expr': '[]',
        'inst_kwargs_expr': '{}',
        'chain_expr': '[]',
        'benchmark': False,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'exception'
    assert out_v2['status'] == 'exception'
    assert out_v1['exc_type'] == 'AttributeError'
    assert out_v2['exc_type'] == 'TypeError'

def test_repro_32_urllib3_util_ssl__create_urllib3_context_return_value_drift():
    """Reproduce return_value_drift (value_or_type_mismatch) on urllib3.util.ssl_.create_urllib3_context.
    Minimal Call: create_urllib3_context()
    """
    payload = {
        'module': 'urllib3.util.ssl_',
        'qualname': 'create_urllib3_context',
        'callable_kind': 'function',
        'args_expr': '[]',
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

def test_repro_33_urllib3_util_ssl__create_urllib3_context_exception_type_drift():
    """Reproduce exception_type_drift (fail_to_pass) on urllib3.util.ssl_.create_urllib3_context.
    Minimal Call: create_urllib3_context('1')
    """
    payload = {
        'module': 'urllib3.util.ssl_',
        'qualname': 'create_urllib3_context',
        'callable_kind': 'function',
        'args_expr': "['1']",
        'kwargs_expr': '{}',
        'inst_args_expr': '[]',
        'inst_kwargs_expr': '{}',
        'chain_expr': '[]',
        'benchmark': False,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'exception'
    assert out_v2['status'] == 'ok'
    assert out_v1['exc_type'] == 'TypeError'

def test_repro_34_urllib3_util_ssl__create_urllib3_context_exception_type_drift():
    """Reproduce exception_type_drift (fail_to_pass) on urllib3.util.ssl_.create_urllib3_context.
    Minimal Call: create_urllib3_context(1)
    """
    payload = {
        'module': 'urllib3.util.ssl_',
        'qualname': 'create_urllib3_context',
        'callable_kind': 'function',
        'args_expr': '[1]',
        'kwargs_expr': '{}',
        'inst_args_expr': '[]',
        'inst_kwargs_expr': '{}',
        'chain_expr': '[]',
        'benchmark': False,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'exception'
    assert out_v2['status'] == 'ok'
    assert out_v1['exc_type'] == 'ValueError'

def test_repro_35_urllib3_util_ssl__ssl_wrap_socket_exception_type_drift():
    """Reproduce exception_type_drift (exception_class_changed) on urllib3.util.ssl_.ssl_wrap_socket.
    Minimal Call: ssl_wrap_socket('', None, None, None, None, None, '1')
    """
    payload = {
        'module': 'urllib3.util.ssl_',
        'qualname': 'ssl_wrap_socket',
        'callable_kind': 'function',
        'args_expr': "['', None, None, None, None, None, '1']",
        'kwargs_expr': '{}',
        'inst_args_expr': '[]',
        'inst_kwargs_expr': '{}',
        'chain_expr': '[]',
        'benchmark': False,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'exception'
    assert out_v2['status'] == 'exception'
    assert out_v1['exc_type'] == 'TypeError'
    assert out_v2['exc_type'] == 'AttributeError'
