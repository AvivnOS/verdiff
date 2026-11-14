# VerDiff Differential Analysis: `packaging` (`21.3` -> `23.2`)

## 1. Executive Telemetry Summary

| Metric | Value |
| :--- | :--- |
| **Package** | `packaging` |
| **Version A (Baseline)** | `21.3` |
| **Version B (Target)** | `23.2` |
| **Python Runtime** | `3.12.14` |
| **Deterministic Seed** | `42` |
| **Public Callables (`v1` / `v2`)** | `21` / `18` |
| **Unchanged Signatures** | `9` |
| **Static Signature Changes** | `12` |
| **Callables Fuzzed** | `17` |
| **Synthesized Inputs Executed** | `538` |
| **Silent Behavioral Drifts Found** | **`6`** |
| **Wall-Clock Duration** | `0.49s` |

## 2. Static API Surface Changes (13)

| Change Kind | Module | Symbol (`v1` -> `v2`) | Signature / Details |
| :--- | :--- | :--- | :--- |
| `signature_changed` | `packaging.specifiers` | `BaseSpecifier.filter` | parameter 'iterable' type annotation changed (Iterable[~VersionTypeVar] -> Iterable[~UnparsedVersionVar]); return annotation changed (Iterable[~VersionTypeVar] -> Iterator[~UnparsedVersionVar]) |
| `signature_changed` | `packaging.specifiers` | `Specifier.contains` | parameter 'item' type annotation changed (Union[packaging.version.Version, packaging.version.LegacyVersion, str] -> Union[packaging.version.Version, str]) |
| `signature_changed` | `packaging.specifiers` | `Specifier.filter` | parameter 'iterable' type annotation changed (Iterable[~VersionTypeVar] -> Iterable[~UnparsedVersionVar]); return annotation changed (Iterable[~VersionTypeVar] -> Iterator[~UnparsedVersionVar]) |
| `signature_changed` | `packaging.specifiers` | `SpecifierSet.contains` | parameter count changed (2 -> 3) |
| `signature_changed` | `packaging.specifiers` | `SpecifierSet.filter` | parameter 'iterable' type annotation changed (Iterable[~VersionTypeVar] -> Iterable[~UnparsedVersionVar]); return annotation changed (Iterable[~VersionTypeVar] -> Iterator[~UnparsedVersionVar]) |
| `signature_changed` | `packaging.utils` | `canonicalize_name` | parameter count changed (1 -> 2) |
| `signature_changed` | `packaging.utils` | `canonicalize_version` | parameter count changed (1 -> 2) |
| `signature_changed` | `packaging.version` | `parse` | return annotation changed (Union[ForwardRef('LegacyVersion'), ForwardRef('Version')] -> Version) |
| `removed` | `packaging.specifiers` | `LegacySpecifier` | Removed public class 'packaging.specifiers.LegacySpecifier' |
| `removed` | `packaging.specifiers` | `LegacySpecifier.contains` | Removed public method 'packaging.specifiers.LegacySpecifier.contains' |
| `removed` | `packaging.specifiers` | `LegacySpecifier.filter` | Removed public method 'packaging.specifiers.LegacySpecifier.filter' |
| `removed` | `packaging.version` | `LegacyVersion` | Removed public class 'packaging.version.LegacyVersion' |
| `added` | `packaging.utils` | `is_normalized_name` | Added public function 'packaging.utils.is_normalized_name' |

## 3. Discovered Behavioral Drifts (6)

### 3.1 `packaging.specifiers.Specifier(spec: str = '', prereleases: Optional[bool] = None) -> Specifier`
- **Drift Category:** `return_value_drift` (`value_or_type_mismatch`)
- **Summary:** Return object state drift on <Specifier('===1.')> (packaging.specifiers.Specifier): attribute 'prereleases' changed (False -> 'InvalidVersion')
- **Input Strategy:** `edge_sweep_positional`
- **Original Fuzzed Call:** `Specifier('===1.0-legacy')`
- **Shrunk Minimal Call (3 shrink steps):** `Specifier('===1.')`
- **Baseline (`21.3`):** `RETURN <Specifier('===1.')> (type: packaging.specifiers.Specifier)`
- **Target (`23.2`):** `RETURN <Specifier('===1.')> (type: packaging.specifiers.Specifier)`

### 3.2 `packaging.specifiers.SpecifierSet(specifiers: str = '', prereleases: Optional[bool] = None) -> SpecifierSet`
- **Drift Category:** `return_value_drift` (`value_or_type_mismatch`)
- **Summary:** Return object state drift on <SpecifierSet('===1.')> (packaging.specifiers.SpecifierSet): attribute 'prereleases' changed (False -> 'InvalidVersion')
- **Input Strategy:** `edge_sweep_positional`
- **Original Fuzzed Call:** `SpecifierSet('===1.0-legacy')`
- **Shrunk Minimal Call (3 shrink steps):** `SpecifierSet('===1.')`
- **Baseline (`21.3`):** `RETURN <SpecifierSet('===1.')> (type: packaging.specifiers.SpecifierSet)`
- **Target (`23.2`):** `RETURN <SpecifierSet('===1.')> (type: packaging.specifiers.SpecifierSet)`

### 3.3 `packaging.specifiers.SpecifierSet.contains(item: Union[packaging.version.Version, packaging.version.LegacyVersion, str], prereleases: Optional[bool] = None) -> bool`
- **Drift Category:** `exception_type_drift` (`pass_to_fail`)
- **Summary:** v1 returned True (builtins.bool), but v2 raised InvalidVersion: Invalid version: ''
- **Input Strategy:** `baseline_required`
- **Original Fuzzed Call:** `SpecifierSet.contains(',')`
- **Shrunk Minimal Call (1 shrink steps):** `SpecifierSet.contains('')`
- **Baseline (`21.3`):** `RETURN True (type: builtins.bool)`
- **Target (`23.2`):** `RAISE InvalidVersion: Invalid version: ''`

### 3.4 `packaging.specifiers.SpecifierSet.filter(iterable: Iterable[~VersionTypeVar], prereleases: Optional[bool] = None) -> Iterable[~VersionTypeVar]`
- **Drift Category:** `return_value_drift` (`value_or_type_mismatch`)
- **Summary:** Return value drift: v1 returned [] (builtins.list) != v2 returned <list_iterator object at 0xADDR> (builtins.list_iterator)
- **Input Strategy:** `baseline_required`
- **Original Fuzzed Call:** `SpecifierSet.filter([])`
- **Shrunk Minimal Call (0 shrink steps):** `SpecifierSet.filter([])`
- **Baseline (`21.3`):** `RETURN [] (type: builtins.list)`
- **Target (`23.2`):** `RETURN <list_iterator object at 0xADDR> (type: builtins.list_iterator)`

### 3.5 `packaging.specifiers.SpecifierSet.filter(iterable: Iterable[~VersionTypeVar], prereleases: Optional[bool] = None) -> Iterable[~VersionTypeVar]`
- **Drift Category:** `exception_type_drift` (`pass_to_fail`)
- **Summary:** v1 returned [] (builtins.list), but v2 raised InvalidVersion: Invalid version: ''
- **Input Strategy:** `edge_sweep_required`
- **Original Fuzzed Call:** `SpecifierSet.filter(['a', 'b', 'c'])`
- **Shrunk Minimal Call (2 shrink steps):** `SpecifierSet.filter([''])`
- **Baseline (`21.3`):** `RETURN [] (type: builtins.list)`
- **Target (`23.2`):** `RAISE InvalidVersion: Invalid version: ''`

### 3.6 `packaging.version.parse(version: str) -> Union[ForwardRef('LegacyVersion'), ForwardRef('Version')]`
- **Drift Category:** `exception_type_drift` (`pass_to_fail`)
- **Summary:** v1 returned <LegacyVersion('')> (packaging.version.LegacyVersion), but v2 raised InvalidVersion: Invalid version: ''
- **Input Strategy:** `edge_sweep_required`
- **Original Fuzzed Call:** `parse('שלום עולם \u202eRTL\u202c')`
- **Shrunk Minimal Call (1 shrink steps):** `parse('')`
- **Baseline (`21.3`):** `RETURN <LegacyVersion('')> (type: packaging.version.LegacyVersion)`
- **Target (`23.2`):** `RAISE InvalidVersion: Invalid version: ''`
