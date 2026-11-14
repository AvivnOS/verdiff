# VerDiff Differential Analysis: `packaging` (`23.1` -> `23.2`)

## 1. Executive Telemetry Summary

| Metric | Value |
| :--- | :--- |
| **Package** | `packaging` |
| **Version A (Baseline)** | `23.1` |
| **Version B (Target)** | `23.2` |
| **Python Runtime** | `3.12.14` |
| **Deterministic Seed** | `42` |
| **Public Callables (`v1` / `v2`)** | `31` / `35` |
| **Unchanged Signatures** | `30` |
| **Static Signature Changes** | `1` |
| **Callables & Chains Fuzzed** | `34` |
| **Synthesized Inputs Executed** | `1563` |
| **Non-Breaking Object Noise Filtered** | `0` |
| **Max Drifts Ceiling (`--max-drifts`)** | `Unlimited (0)` |
| **Silent Behavioral Drifts Found** | **`5`** |
| **Wall-Clock Duration** | `1.65s` |

## 2. Static API Surface Changes (5)

| Change Kind | Module | Symbol (`v1` -> `v2`) | Signature / Details |
| :--- | :--- | :--- | :--- |
| `signature_changed` | `packaging.utils` | `canonicalize_name` | parameter count changed (1 -> 2) |
| `added` | `packaging.metadata` | `Metadata` | Added public class 'packaging.metadata.Metadata' |
| `added` | `packaging.metadata` | `Metadata.from_email` | Added public classmethod 'packaging.metadata.Metadata.from_email' |
| `added` | `packaging.metadata` | `Metadata.from_raw` | Added public classmethod 'packaging.metadata.Metadata.from_raw' |
| `added` | `packaging.utils` | `is_normalized_name` | Added public function 'packaging.utils.is_normalized_name' |

## 3. Discovered Behavioral Drifts (5)

### 3.1 `packaging.markers.Marker(marker: str) -> Marker`
- **Drift Category:** `exception_type_drift` (`pass_to_fail`)
- **Summary:** v1 returned <Marker('os_name == "a"')> (packaging.markers.Marker), but v2 raised InvalidMarker: Expected end of marker expression
    os_name == "a" b
                   ^
- **Input Strategy:** `edge_sweep_required`
- **Original Fuzzed Call:** `Marker('os_name == "a" b')`
- **Shrunk Minimal Call (0 shrink steps):** `Marker('os_name == "a" b')`
- **Baseline (`23.1`):** `RETURN <Marker('os_name == "a"')> (type: packaging.markers.Marker)`
- **Target (`23.2`):** `RAISE InvalidMarker: Expected end of marker expression
    os_name == "a" b
                   ^`

### 3.2 `packaging.requirements.Requirement(requirement_string: str) -> Requirement`
- **Drift Category:** `exception_type_drift` (`fail_to_pass`)
- **Summary:** v1 raised InvalidRequirement (Invalid URL: h), but v2 returned <Requirement('g@ h')> (packaging.requirements.Requirement)
- **Input Strategy:** `edge_sweep_required`
- **Original Fuzzed Call:** `Requirement('pkg @ http:///path')`
- **Shrunk Minimal Call (5 shrink steps):** `Requirement('g @ h')`
- **Baseline (`23.1`):** `RAISE InvalidRequirement: Invalid URL: h`
- **Target (`23.2`):** `RETURN <Requirement('g@ h')> (type: packaging.requirements.Requirement)`

### 3.3 `packaging.markers.Marker.evaluate(environment: Optional[Dict[str, str]] = None) -> bool`
- **Drift Category:** `exception_type_drift` (`pass_to_fail`)
- **Summary:** v1 returned False (builtins.bool), but v2 raised InvalidMarker: Expected end of marker expression
    os_name == "a" b
                   ^
- **Input Strategy:** `defaults_only`
- **Original Fuzzed Call:** `Marker('os_name == "a" b').evaluate()`
- **Shrunk Minimal Call (0 shrink steps):** `Marker('os_name == "a" b').evaluate()`
- **Baseline (`23.1`):** `RETURN False (type: builtins.bool)`
- **Target (`23.2`):** `RAISE InvalidMarker: Expected end of marker expression
    os_name == "a" b
                   ^`

### 3.4 `packaging.markers.Marker.evaluate(environment: Optional[Dict[str, str]] = None) -> bool`
- **Drift Category:** `exception_type_drift` (`exception_class_changed`)
- **Summary:** Exception type changed from ValueError ('dictionary update sequence element #0 has length 1; 2 is required') in v1 to InvalidMarker ('Expected end of marker expression
    os_name == "a" b
                   ^') in v2
- **Input Strategy:** `edge_sweep_positional`
- **Original Fuzzed Call:** `Marker('os_name == "a" b').evaluate('_diff')`
- **Shrunk Minimal Call (2 shrink steps):** `Marker('os_name == "a" b').evaluate('_')`
- **Baseline (`23.1`):** `RAISE ValueError: dictionary update sequence element #0 has length 1; 2 is required`
- **Target (`23.2`):** `RAISE InvalidMarker: Expected end of marker expression
    os_name == "a" b
                   ^`

### 3.5 `packaging.markers.Marker.evaluate(environment: Optional[Dict[str, str]] = None) -> bool`
- **Drift Category:** `exception_type_drift` (`exception_class_changed`)
- **Summary:** Exception type changed from TypeError (''int' object is not iterable') in v1 to InvalidMarker ('Expected end of marker expression
    os_name == "a" b
                   ^') in v2
- **Input Strategy:** `edge_sweep_positional`
- **Original Fuzzed Call:** `Marker('os_name == "a" b').evaluate(0)`
- **Shrunk Minimal Call (0 shrink steps):** `Marker('os_name == "a" b').evaluate(0)`
- **Baseline (`23.1`):** `RAISE TypeError: 'int' object is not iterable`
- **Target (`23.2`):** `RAISE InvalidMarker: Expected end of marker expression
    os_name == "a" b
                   ^`
