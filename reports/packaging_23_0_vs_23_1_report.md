# VerDiff Differential Analysis: `packaging` (`23.0` -> `23.1`)

## 1. Executive Telemetry Summary

| Metric | Value |
| :--- | :--- |
| **Package** | `packaging` |
| **Version A (Baseline)** | `23.0` |
| **Version B (Target)** | `23.1` |
| **Python Runtime** | `3.12.14` |
| **Deterministic Seed** | `42` |
| **Public Callables (`v1` / `v2`)** | `31` / `31` |
| **Unchanged Signatures** | `30` |
| **Static Signature Changes** | `1` |
| **Callables & Chains Fuzzed** | `33` |
| **Synthesized Inputs Executed** | `1514` |
| **Non-Breaking Object Noise Filtered** | `0` |
| **Max Drifts Ceiling (`--max-drifts`)** | `Unlimited (0)` |
| **Silent Behavioral Drifts Found** | **`0`** |
| **Wall-Clock Duration** | `1.66s` |

## 2. Static API Surface Changes (2)

| Change Kind | Module | Symbol (`v1` -> `v2`) | Signature / Details |
| :--- | :--- | :--- | :--- |
| `removed` | `packaging.requirements` | `parse_requirement` | Removed public function 'packaging.requirements.parse_requirement' |
| `added` | `packaging.metadata` | `parse_email` | Added public function 'packaging.metadata.parse_email' |

## 3. Discovered Behavioral Drifts (0)

_No behavioral drifts detected across fuzzed inputs._
