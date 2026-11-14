r"""Standalone pytest regression suite for urllib3 (2.0.2 -> 2.0.7).

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
VERSION_V1 = '2.0.2'
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

def test_repro_01_urllib3_connection_httpconnection_return_value_drift():
    """Reproduce return_value_drift (value_or_type_mismatch) on urllib3.connection.HTTPConnection.
    Minimal Call: HTTPConnection('', 0)
    """
    payload = {
        'module': 'urllib3.connection',
        'qualname': 'HTTPConnection',
        'callable_kind': 'class',
        'args_expr': "['', 0]",
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

def test_repro_02_urllib3_connection_httpsconnection_return_value_drift():
    """Reproduce return_value_drift (value_or_type_mismatch) on urllib3.connection.HTTPSConnection.
    Minimal Call: HTTPSConnection('', 0)
    """
    payload = {
        'module': 'urllib3.connection',
        'qualname': 'HTTPSConnection',
        'callable_kind': 'class',
        'args_expr': "['', 0]",
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

def test_repro_03_urllib3_connection_verifiedhttpsconnection_return_value_drift():
    """Reproduce return_value_drift (value_or_type_mismatch) on urllib3.connection.VerifiedHTTPSConnection.
    Minimal Call: VerifiedHTTPSConnection('', 0)
    """
    payload = {
        'module': 'urllib3.connection',
        'qualname': 'VerifiedHTTPSConnection',
        'callable_kind': 'class',
        'args_expr': "['', 0]",
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

def test_repro_04_urllib3_connectionpool_httpconnectionpool_return_value_drift():
    """Reproduce return_value_drift (value_or_type_mismatch) on urllib3.connectionpool.HTTPConnectionPool.
    Minimal Call: HTTPConnectionPool('h')
    """
    payload = {
        'module': 'urllib3.connectionpool',
        'qualname': 'HTTPConnectionPool',
        'callable_kind': 'class',
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

def test_repro_05_urllib3_connectionpool_httpsconnectionpool_return_value_drift():
    """Reproduce return_value_drift (value_or_type_mismatch) on urllib3.connectionpool.HTTPSConnectionPool.
    Minimal Call: HTTPSConnectionPool('h')
    """
    payload = {
        'module': 'urllib3.connectionpool',
        'qualname': 'HTTPSConnectionPool',
        'callable_kind': 'class',
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

def test_repro_06_urllib3_poolmanager_poolmanager_stateful_chain__return_value_drift():
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

def test_repro_07_urllib3_poolmanager_proxymanager_stateful_chain__return_value_drift():
    """Reproduce return_value_drift (value_or_type_mismatch) on urllib3.poolmanager.ProxyManager.<stateful_chain>.
    Minimal Call: obj = ProxyManager('https://example.com/path?a=1&b=2#sec'); obj.connection_from_host('')
    """
    payload = {
        'module': 'urllib3.poolmanager',
        'qualname': 'ProxyManager.<stateful_chain>',
        'callable_kind': 'stateful_chain',
        'args_expr': '[]',
        'kwargs_expr': '{}',
        'inst_args_expr': "['https://example.com/path?a=1&b=2#sec']",
        'inst_kwargs_expr': '{}',
        'chain_expr': "[('connection_from_host', [''], {})]",
        'benchmark': False,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'ok' and out_v2['status'] == 'ok'
    assert (out_v1['type'], out_v1['repr'], out_v1['state']) != (out_v2['type'], out_v2['repr'], out_v2['state'])

def test_repro_08_urllib3_util_retry_retry_return_value_drift():
    """Reproduce return_value_drift (value_or_type_mismatch) on urllib3.util.retry.Retry.
    Minimal Call: Retry()
    """
    payload = {
        'module': 'urllib3.util.retry',
        'qualname': 'Retry',
        'callable_kind': 'class',
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

def test_repro_09_urllib3_util_retry_retry_stateful_chain__return_value_drift():
    """Reproduce return_value_drift (value_or_type_mismatch) on urllib3.util.retry.Retry.<stateful_chain>.
    Minimal Call: obj = Retry(); obj.increment()
    """
    payload = {
        'module': 'urllib3.util.retry',
        'qualname': 'Retry.<stateful_chain>',
        'callable_kind': 'stateful_chain',
        'args_expr': '[]',
        'kwargs_expr': '{}',
        'inst_args_expr': '[]',
        'inst_kwargs_expr': '{}',
        'chain_expr': "[('increment', [], {})]",
        'benchmark': False,
    }
    out_v1 = _invoke_standalone(VERSION_V1, payload)
    out_v2 = _invoke_standalone(VERSION_V2, payload)
    assert out_v1['status'] == 'ok' and out_v2['status'] == 'ok'
    assert (out_v1['type'], out_v1['repr'], out_v1['state']) != (out_v2['type'], out_v2['repr'], out_v2['state'])
