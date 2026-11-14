"""Deterministic tagged wire codec and structural canonicalizer for IPC and oracle comparison."""

from __future__ import annotations

import base64
import datetime
import decimal
import math
import pathlib
import re
import uuid
from typing import Any

_MEMORY_ADDR_RE = re.compile(r"(?: at 0x[0-9a-fA-F]+>| @ \d+>)")
_SENTINEL_RE = re.compile(
    r"(?:<object object at 0xADDR>|<_TYPE_DEFAULT\.token:\s*-?\d+>|<_[A-Za-z0-9_]*DEFAULT[A-Za-z0-9_.]*(?::\s*[^>]+)?>|<Sentinel[^>]*>)"
)


def strip_memory_addresses(text: str) -> str:
    """Remove volatile CPython object memory addresses (hex or decimal id) from repr strings."""
    return _MEMORY_ADDR_RE.sub(" at 0xADDR>", text)


def normalize_sentinel_repr(text: str) -> str:
    """Normalize internal library default sentinel representations to a canonical token."""
    return _SENTINEL_RE.sub("<SENTINEL>", strip_memory_addresses(text))


def is_internal_sentinel_object(val: Any) -> bool:
    """Return True if val is a bare object() sentinel or private default enum token."""
    cls = type(val)
    if cls is object:
        return True
    qual = cls.__qualname__
    mod = cls.__module__
    if qual.startswith("_") and any(
        tok in qual.upper() for tok in ("DEFAULT", "SENTINEL", "MISSING", "UNSET", "NOVALUE", "EMPTY")
    ):
        return True
    if mod.startswith("_") and qual.upper() in ("TOKEN", "SENTINEL", "DEFAULT"):
        return True
    return False


def encode_value(val: Any, _depth: int = 0) -> dict[str, Any]:
    """Encode an arbitrary Python value into a JSON-safe tagged dictionary."""
    if _depth > 16:
        return {"__t__": "max_depth", "v": strip_memory_addresses(repr(val))[:200]}

    if val is None:
        return {"__t__": "none"}
    if val is True or val is False:
        return {"__t__": "bool", "v": bool(val)}
    if type(val) is int:
        return {"__t__": "int", "v": val}
    if type(val) is float:
        if math.isnan(val):
            return {"__t__": "float_special", "v": "nan"}
        if math.isinf(val):
            return {"__t__": "float_special", "v": "inf" if val > 0 else "-inf"}
        if val == 0.0 and math.copysign(1.0, val) < 0:
            return {"__t__": "float_special", "v": "-0.0"}
        return {"__t__": "float", "v": val}
    if type(val) is str:
        return {"__t__": "str", "v": val}
    if type(val) is bytes:
        return {"__t__": "bytes", "v": base64.b64encode(val).decode("ascii")}
    if type(val) is bytearray:
        return {"__t__": "bytearray", "v": base64.b64encode(bytes(val)).decode("ascii")}
    if type(val) is list:
        return {"__t__": "list", "v": [encode_value(x, _depth + 1) for x in val]}
    if type(val) is tuple:
        return {"__t__": "tuple", "v": [encode_value(x, _depth + 1) for x in val]}
    if type(val) is set:
        items = [encode_value(x, _depth + 1) for x in val]
        items.sort(key=lambda item: repr(item))
        return {"__t__": "set", "v": items}
    if type(val) is frozenset:
        items = [encode_value(x, _depth + 1) for x in val]
        items.sort(key=lambda item: repr(item))
        return {"__t__": "frozenset", "v": items}
    if type(val) is dict:
        pairs = [
            [encode_value(k, _depth + 1), encode_value(v, _depth + 1)]
            for k, v in val.items()
        ]
        return {"__t__": "dict", "v": pairs}
    if isinstance(val, datetime.datetime):
        return {"__t__": "datetime", "v": val.isoformat()}
    if isinstance(val, datetime.date):
        return {"__t__": "date", "v": val.isoformat()}
    if isinstance(val, datetime.time):
        return {"__t__": "time", "v": val.isoformat()}
    if isinstance(val, datetime.timedelta):
        return {
            "__t__": "timedelta",
            "v": [val.days, val.seconds, val.microseconds],
        }
    if isinstance(val, decimal.Decimal):
        return {"__t__": "decimal", "v": str(val)}
    if isinstance(val, pathlib.PurePath):
        return {"__t__": "path", "v": str(val)}
    if isinstance(val, uuid.UUID):
        return {"__t__": "uuid", "v": str(val)}
    if isinstance(val, re.Pattern):
        return {"__t__": "regex", "v": [val.pattern, val.flags]}
    if isinstance(val, slice):
        return {
            "__t__": "slice",
            "v": [
                encode_value(val.start, _depth + 1),
                encode_value(val.stop, _depth + 1),
                encode_value(val.step, _depth + 1),
            ],
        }

    if is_internal_sentinel_object(val):
        return {"__t__": "sentinel", "repr": _safe_repr(val)}

    cls = type(val)
    type_fqn = f"{cls.__module__}.{cls.__qualname__}"
    state = extract_object_state(val, _depth + 1)
    return {
        "__t__": "object",
        "cls": type_fqn,
        "str": _safe_str(val),
        "repr": _safe_repr(val),
        "state": state,
    }


def _safe_str(val: Any) -> str:
    try:
        return strip_memory_addresses(str(val))[:500]
    except Exception as exc:
        return f"<str_error:{type(exc).__name__}>"


def _safe_repr(val: Any) -> str:
    try:
        return strip_memory_addresses(repr(val))[:500]
    except Exception as exc:
        return f"<repr_error:{type(exc).__name__}>"


def extract_object_state(val: Any, _depth: int = 0) -> dict[str, Any]:
    """Extract deterministic public state of a custom object or builtin subclass."""
    if _depth > 10:
        return {}
    state: dict[str, Any] = {}
    if isinstance(val, (str, bytes, int, float)):
        state["__primitive_base__"] = encode_value(
            str(val)
            if isinstance(val, str)
            else (
                bytes(val)
                if isinstance(val, bytes)
                else (int(val) if isinstance(val, int) else float(val))
            ),
            _depth + 1,
        )
    if isinstance(val, (list, tuple, set, frozenset)) and type(val) not in (list, tuple, set, frozenset):
        if hasattr(val, "_fields"):
            for field_name in getattr(val, "_fields", ()):
                try:
                    state[field_name] = encode_value(getattr(val, field_name), _depth + 1)
                except Exception as exc:
                    state[field_name] = {"__t__": "prop_exc", "v": type(exc).__name__}
            return state
        try:
            state["__items__"] = [encode_value(x, _depth + 1) for x in list(val)[:64]]
        except Exception:
            pass
    if isinstance(val, dict) and type(val) is not dict:
        try:
            state["__items__"] = [
                [encode_value(k, _depth + 1), encode_value(v, _depth + 1)]
                for k, v in list(val.items())[:64]
            ]
        except Exception:
            pass

    seen_attrs: set[str] = set()
    if hasattr(val, "__dict__"):
        try:
            for k, v in sorted(vars(val).items()):
                if not k.startswith("_") and not callable(v):
                    seen_attrs.add(k)
                    state[k] = encode_value(v, _depth + 1)
        except Exception:
            pass

    cls = type(val)
    for base in cls.__mro__:
        slots = getattr(base, "__slots__", ())
        if isinstance(slots, str):
            slots = (slots,)
        for slot in slots:
            if slot.startswith("_") or slot in seen_attrs:
                continue
            if hasattr(val, slot):
                try:
                    slot_val = getattr(val, slot)
                    if not callable(slot_val):
                        state[slot] = encode_value(slot_val, _depth + 1)
                        seen_attrs.add(slot)
                except Exception:
                    pass

    for attr_name in sorted(dir(cls)):
        if attr_name.startswith("_") or attr_name in seen_attrs:
            continue
        try:
            cls_attr = getattr(cls, attr_name, None)
            if isinstance(cls_attr, property):
                prop_val = getattr(val, attr_name)
                state[attr_name] = encode_value(prop_val, _depth + 1)
                seen_attrs.add(attr_name)
        except Exception as exc:
            state[attr_name] = {"__t__": "prop_exc", "v": type(exc).__name__}

    # If object has public iterability (e.g. custom container/set/queue), capture items snapshot
    if not state and hasattr(val, "__iter__") and not isinstance(val, (str, bytes, bytearray)):
        try:
            state["__iter_items__"] = [encode_value(x, _depth + 1) for x in list(val)[:64]]
        except Exception:
            pass

    if not state and " at 0xADDR>" in _safe_repr(val) and hasattr(val, "__dict__"):
        try:
            for k, v in sorted(vars(val).items()):
                if k.startswith("_") and not k.startswith("__") and not callable(v):
                    state[k] = encode_value(v, _depth + 1)
        except Exception:
            pass

    return state


def decode_value(tagged: Any) -> Any:
    """Decode a tagged dictionary back into a concrete Python object."""
    if not isinstance(tagged, dict) or "__t__" not in tagged:
        return tagged

    tag = tagged["__t__"]
    v = tagged.get("v")
    if tag == "none":
        return None
    if tag == "bool":
        return bool(v)
    if tag == "int":
        return int(v)
    if tag == "float":
        return float(v)
    if tag == "float_special":
        if v == "nan":
            return float("nan")
        if v == "inf":
            return float("inf")
        if v == "-inf":
            return float("-inf")
        if v == "-0.0":
            return -0.0
        return float(v)
    if tag == "str":
        return str(v)
    if tag == "bytes":
        return base64.b64decode(v.encode("ascii"))
    if tag == "bytearray":
        return bytearray(base64.b64decode(v.encode("ascii")))
    if tag == "list":
        return [decode_value(x) for x in v]
    if tag == "tuple":
        return tuple(decode_value(x) for x in v)
    if tag == "set":
        return {decode_value(x) for x in v}
    if tag == "frozenset":
        return frozenset(decode_value(x) for x in v)
    if tag == "dict":
        return {decode_value(k): decode_value(val_item) for k, val_item in v}
    if tag == "datetime":
        return datetime.datetime.fromisoformat(v)
    if tag == "date":
        return datetime.date.fromisoformat(v)
    if tag == "time":
        return datetime.time.fromisoformat(v)
    if tag == "timedelta":
        return datetime.timedelta(days=v[0], seconds=v[1], microseconds=v[2])
    if tag == "decimal":
        return decimal.Decimal(v)
    if tag == "path":
        return pathlib.Path(v)
    if tag == "uuid":
        return uuid.UUID(v)
    if tag == "regex":
        return re.compile(v[0], v[1])
    if tag == "slice":
        return slice(decode_value(v[0]), decode_value(v[1]), decode_value(v[2]))
    return v


def value_to_python_expr(val: Any) -> str:
    """Render a synthesized Python value as a deterministic, valid Python expression for pytest output."""
    if val is None:
        return "None"
    if val is True or val is False:
        return "True" if val else "False"
    if type(val) is int:
        return repr(val)
    if type(val) is float:
        if math.isnan(val):
            return "float('nan')"
        if math.isinf(val):
            return "float('inf')" if val > 0 else "float('-inf')"
        if val == 0.0 and math.copysign(1.0, val) < 0:
            return "-0.0"
        return repr(val)
    if type(val) is str:
        return repr(val)
    if type(val) is bytes:
        return repr(val)
    if type(val) is bytearray:
        return f"bytearray({bytes(val)!r})"
    if type(val) is list:
        return "[" + ", ".join(value_to_python_expr(x) for x in val) + "]"
    if type(val) is tuple:
        if len(val) == 1:
            return f"({value_to_python_expr(val[0])},)"
        return "(" + ", ".join(value_to_python_expr(x) for x in val) + ")"
    if type(val) is set:
        if not val:
            return "set()"
        items = sorted((value_to_python_expr(x) for x in val))
        return "{" + ", ".join(items) + "}"
    if type(val) is frozenset:
        items = sorted((value_to_python_expr(x) for x in val))
        return f"frozenset([{', '.join(items)}])"
    if type(val) is dict:
        pairs = [f"{value_to_python_expr(k)}: {value_to_python_expr(v)}" for k, v in val.items()]
        return "{" + ", ".join(pairs) + "}"
    if isinstance(val, datetime.datetime):
        return f"datetime.datetime.fromisoformat({val.isoformat()!r})"
    if isinstance(val, datetime.date):
        return f"datetime.date.fromisoformat({val.isoformat()!r})"
    if isinstance(val, datetime.time):
        return f"datetime.time.fromisoformat({val.isoformat()!r})"
    if isinstance(val, datetime.timedelta):
        return f"datetime.timedelta(days={val.days}, seconds={val.seconds}, microseconds={val.microseconds})"
    if isinstance(val, decimal.Decimal):
        return f"decimal.Decimal({str(val)!r})"
    if isinstance(val, pathlib.PurePath):
        return f"pathlib.Path({str(val)!r})"
    if isinstance(val, uuid.UUID):
        return f"uuid.UUID({str(val)!r})"
    if isinstance(val, re.Pattern):
        return f"re.compile({val.pattern!r}, {val.flags})"
    if isinstance(val, slice):
        return f"slice({value_to_python_expr(val.start)}, {value_to_python_expr(val.stop)}, {value_to_python_expr(val.step)})"
    return repr(val)
