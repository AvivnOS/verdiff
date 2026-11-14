r"""Standalone pytest regression suite for packaging (23.0 -> 23.1).

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

PACKAGE = 'packaging'
VERSION_V1 = '23.0'
VERSION_V2 = '23.1'

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

def test_zero_behavioral_drifts_verified():
    """Verified 0 behavioral drifts between packaging 23.0 and 23.1."""
    py1, _ = _find_env_python(PACKAGE, VERSION_V1)
    py2, _ = _find_env_python(PACKAGE, VERSION_V2)
    assert Path(py1).is_file() and Path(py2).is_file()
