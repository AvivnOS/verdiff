# VerDiff Differential Analysis: `semver` (`2.13.0` -> `3.0.2`)

## 1. Executive Telemetry Summary

| Metric | Value |
| :--- | :--- |
| **Package** | `semver` |
| **Version A (Baseline)** | `2.13.0` |
| **Version B (Target)** | `3.0.2` |
| **Python Runtime** | `3.12.14` |
| **Deterministic Seed** | `42` |
| **Public Callables (`v1` / `v2`)** | `42` / `53` |
| **Unchanged Signatures** | `13` |
| **Static Signature Changes** | `29` |
| **Callables Fuzzed** | `14` |
| **Synthesized Inputs Executed** | `490` |
| **Silent Behavioral Drifts Found** | **`6`** |
| **Wall-Clock Duration** | `0.56s` |

## 2. Static API Surface Changes (68)

| Change Kind | Module | Symbol (`v1` -> `v2`) | Signature / Details |
| :--- | :--- | :--- | :--- |
| `signature_changed` | `semver` | `compare` | parameter 'ver1' type annotation changed (untyped -> str); parameter 'ver2' type annotation changed (untyped -> str); return annotation changed (untyped -> int) |
| `removed` | `semver` | `VersionInfo` | Removed public class 'semver.VersionInfo' |
| `removed` | `semver` | `VersionInfo.bump_build` | Removed public method 'semver.VersionInfo.bump_build' |
| `removed` | `semver` | `VersionInfo.bump_major` | Removed public method 'semver.VersionInfo.bump_major' |
| `removed` | `semver` | `VersionInfo.bump_minor` | Removed public method 'semver.VersionInfo.bump_minor' |
| `removed` | `semver` | `VersionInfo.bump_patch` | Removed public method 'semver.VersionInfo.bump_patch' |
| `removed` | `semver` | `VersionInfo.bump_prerelease` | Removed public method 'semver.VersionInfo.bump_prerelease' |
| `removed` | `semver` | `VersionInfo.compare` | Removed public method 'semver.VersionInfo.compare' |
| `removed` | `semver` | `VersionInfo.finalize_version` | Removed public method 'semver.VersionInfo.finalize_version' |
| `removed` | `semver` | `VersionInfo.isvalid` | Removed public classmethod 'semver.VersionInfo.isvalid' |
| `removed` | `semver` | `VersionInfo.match` | Removed public method 'semver.VersionInfo.match' |
| `removed` | `semver` | `VersionInfo.next_version` | Removed public method 'semver.VersionInfo.next_version' |
| `removed` | `semver` | `VersionInfo.parse` | Removed public classmethod 'semver.VersionInfo.parse' |
| `removed` | `semver` | `VersionInfo.replace` | Removed public method 'semver.VersionInfo.replace' |
| `removed` | `semver` | `VersionInfo.to_dict` | Removed public method 'semver.VersionInfo.to_dict' |
| `removed` | `semver` | `VersionInfo.to_tuple` | Removed public method 'semver.VersionInfo.to_tuple' |
| `removed` | `semver` | `b` | Removed public function 'semver.b' |
| `removed` | `semver` | `cmd_bump` | Removed public function 'semver.cmd_bump' |
| `removed` | `semver` | `cmd_check` | Removed public function 'semver.cmd_check' |
| `removed` | `semver` | `cmd_compare` | Removed public function 'semver.cmd_compare' |
| `removed` | `semver` | `cmd_nextver` | Removed public function 'semver.cmd_nextver' |
| `removed` | `semver` | `cmp` | Removed public function 'semver.cmp' |
| `removed` | `semver` | `comparator` | Removed public function 'semver.comparator' |
| `removed` | `semver` | `createparser` | Removed public function 'semver.createparser' |
| `removed` | `semver` | `deprecated` | Removed public function 'semver.deprecated' |
| `removed` | `semver` | `ensure_str` | Removed public function 'semver.ensure_str' |
| `removed` | `semver` | `main` | Removed public function 'semver.main' |
| `removed` | `semver` | `process` | Removed public function 'semver.process' |
| `removed` | `semver` | `u` | Removed public function 'semver.u' |
| `added` | `semver.cli` | `cmd_bump` | Added public function 'semver.cli.cmd_bump' |
| `added` | `semver.cli` | `cmd_check` | Added public function 'semver.cli.cmd_check' |
| `added` | `semver.cli` | `cmd_compare` | Added public function 'semver.cli.cmd_compare' |
| `added` | `semver.cli` | `cmd_nextver` | Added public function 'semver.cli.cmd_nextver' |
| `added` | `semver.cli` | `createparser` | Added public function 'semver.cli.createparser' |
| `added` | `semver.cli` | `main` | Added public function 'semver.cli.main' |
| `added` | `semver.cli` | `process` | Added public function 'semver.cli.process' |
| `added` | `semver.version` | `Version` | Added public class 'semver.version.Version' |
| `added` | `semver.version` | `Version.bump_build` | Added public method 'semver.version.Version.bump_build' |
| `added` | `semver.version` | `Version.bump_major` | Added public method 'semver.version.Version.bump_major' |
| `added` | `semver.version` | `Version.bump_minor` | Added public method 'semver.version.Version.bump_minor' |
| `added` | `semver.version` | `Version.bump_patch` | Added public method 'semver.version.Version.bump_patch' |
| `added` | `semver.version` | `Version.bump_prerelease` | Added public method 'semver.version.Version.bump_prerelease' |
| `added` | `semver.version` | `Version.compare` | Added public method 'semver.version.Version.compare' |
| `added` | `semver.version` | `Version.finalize_version` | Added public method 'semver.version.Version.finalize_version' |
| `added` | `semver.version` | `Version.is_compatible` | Added public method 'semver.version.Version.is_compatible' |
| `added` | `semver.version` | `Version.is_valid` | Added public classmethod 'semver.version.Version.is_valid' |
| `added` | `semver.version` | `Version.match` | Added public method 'semver.version.Version.match' |
| `added` | `semver.version` | `Version.next_version` | Added public method 'semver.version.Version.next_version' |
| `added` | `semver.version` | `Version.parse` | Added public classmethod 'semver.version.Version.parse' |
| `added` | `semver.version` | `Version.replace` | Added public method 'semver.version.Version.replace' |
| `added` | `semver.version` | `Version.to_dict` | Added public method 'semver.version.Version.to_dict' |
| `added` | `semver.version` | `Version.to_tuple` | Added public method 'semver.version.Version.to_tuple' |
| `added` | `semver.version` | `VersionInfo` | Added public class 'semver.version.VersionInfo' |
| `added` | `semver.version` | `VersionInfo.bump_build` | Added public method 'semver.version.VersionInfo.bump_build' |
| `added` | `semver.version` | `VersionInfo.bump_major` | Added public method 'semver.version.VersionInfo.bump_major' |
| `added` | `semver.version` | `VersionInfo.bump_minor` | Added public method 'semver.version.VersionInfo.bump_minor' |
| `added` | `semver.version` | `VersionInfo.bump_patch` | Added public method 'semver.version.VersionInfo.bump_patch' |
| `added` | `semver.version` | `VersionInfo.bump_prerelease` | Added public method 'semver.version.VersionInfo.bump_prerelease' |
| `added` | `semver.version` | `VersionInfo.compare` | Added public method 'semver.version.VersionInfo.compare' |
| `added` | `semver.version` | `VersionInfo.finalize_version` | Added public method 'semver.version.VersionInfo.finalize_version' |
| `added` | `semver.version` | `VersionInfo.is_compatible` | Added public method 'semver.version.VersionInfo.is_compatible' |
| `added` | `semver.version` | `VersionInfo.is_valid` | Added public classmethod 'semver.version.VersionInfo.is_valid' |
| `added` | `semver.version` | `VersionInfo.match` | Added public method 'semver.version.VersionInfo.match' |
| `added` | `semver.version` | `VersionInfo.next_version` | Added public method 'semver.version.VersionInfo.next_version' |
| `added` | `semver.version` | `VersionInfo.parse` | Added public classmethod 'semver.version.VersionInfo.parse' |
| `added` | `semver.version` | `VersionInfo.replace` | Added public method 'semver.version.VersionInfo.replace' |
| `added` | `semver.version` | `VersionInfo.to_dict` | Added public method 'semver.version.VersionInfo.to_dict' |
| `added` | `semver.version` | `VersionInfo.to_tuple` | Added public method 'semver.version.VersionInfo.to_tuple' |

## 3. Discovered Behavioral Drifts (6)

### 3.1 `semver.bump_build(version, token = 'build')`
- **Drift Category:** `return_value_drift` (`value_or_type_mismatch`)
- **Summary:** Return value drift: v1 returned '1.0.0+build.1' (builtins.str) != v2 returned '1.0.0+1' (builtins.str)
- **Input Strategy:** `edge_sweep_positional`
- **Original Fuzzed Call:** `bump_build('1.0.0', '')`
- **Shrunk Minimal Call (0 shrink steps):** `bump_build('1.0.0', '')`
- **Baseline (`2.13.0`):** `RETURN '1.0.0+build.1' (type: builtins.str)`
- **Target (`3.0.2`):** `RETURN '1.0.0+1' (type: builtins.str)`

### 3.2 `semver.bump_build(version, token = 'build')`
- **Drift Category:** `exception_type_drift` (`fail_to_pass`)
- **Summary:** v1 raised TypeError (can't concat str to bytes), but v2 returned "1.0.0+b'b'.1" (builtins.str)
- **Input Strategy:** `edge_sweep_positional`
- **Original Fuzzed Call:** `bump_build('1.0.0', b'bytes')`
- **Shrunk Minimal Call (2 shrink steps):** `bump_build('1.0.0', b'b')`
- **Baseline (`2.13.0`):** `RAISE TypeError: can't concat str to bytes`
- **Target (`3.0.2`):** `RETURN "1.0.0+b'b'.1" (type: builtins.str)`

### 3.3 `semver.bump_prerelease(version, token = 'rc')`
- **Drift Category:** `return_value_drift` (`value_or_type_mismatch`)
- **Summary:** Return value drift: v1 returned '1.0.0-rc.1' (builtins.str) != v2 returned '1.0.0-1' (builtins.str)
- **Input Strategy:** `edge_sweep_positional`
- **Original Fuzzed Call:** `bump_prerelease('1.0.0', '')`
- **Shrunk Minimal Call (0 shrink steps):** `bump_prerelease('1.0.0', '')`
- **Baseline (`2.13.0`):** `RETURN '1.0.0-rc.1' (type: builtins.str)`
- **Target (`3.0.2`):** `RETURN '1.0.0-1' (type: builtins.str)`

### 3.4 `semver.bump_prerelease(version, token = 'rc')`
- **Drift Category:** `exception_type_drift` (`fail_to_pass`)
- **Summary:** v1 raised TypeError (can't concat str to bytes), but v2 returned "1.0.0-b'b'.1" (builtins.str)
- **Input Strategy:** `edge_sweep_positional`
- **Original Fuzzed Call:** `bump_prerelease('1.0.0', b'bytes')`
- **Shrunk Minimal Call (2 shrink steps):** `bump_prerelease('1.0.0', b'b')`
- **Baseline (`2.13.0`):** `RAISE TypeError: can't concat str to bytes`
- **Target (`3.0.2`):** `RETURN "1.0.0-b'b'.1" (type: builtins.str)`

### 3.5 `semver.parse(version)`
- **Drift Category:** `return_value_drift` (`value_or_type_mismatch`)
- **Summary:** Return value drift: v1 returned OrderedDict({'major': 1, 'minor': 0, 'patch': 0, 'prerelease': None, 'build': None}) (collections.OrderedDict) != v2 returned {'major': 1, 'minor': 0, 'patch': 0, 'prerelease': None, 'build': None} (builtins.dict)
- **Input Strategy:** `baseline_required`
- **Original Fuzzed Call:** `parse('1.0.0')`
- **Shrunk Minimal Call (0 shrink steps):** `parse('1.0.0')`
- **Baseline (`2.13.0`):** `RETURN OrderedDict({'major': 1, 'minor': 0, 'patch': 0, 'prerelease': None, 'build': None}) (type: collections.OrderedDict)`
- **Target (`3.0.2`):** `RETURN {'major': 1, 'minor': 0, 'patch': 0, 'prerelease': None, 'build': None} (type: builtins.dict)`

### 3.6 `semver.parse_version_info(version)`
- **Drift Category:** `return_value_drift` (`value_or_type_mismatch`)
- **Summary:** Return value drift: v1 returned VersionInfo(major=1, minor=0, patch=0, prerelease=None, build=None) (semver.VersionInfo) != v2 returned Version(major=1, minor=0, patch=0, prerelease=None, build=None) (semver.version.Version)
- **Input Strategy:** `baseline_required`
- **Original Fuzzed Call:** `parse_version_info('1.0.0')`
- **Shrunk Minimal Call (0 shrink steps):** `parse_version_info('1.0.0')`
- **Baseline (`2.13.0`):** `RETURN VersionInfo(major=1, minor=0, patch=0, prerelease=None, build=None) (type: semver.VersionInfo)`
- **Target (`3.0.2`):** `RETURN Version(major=1, minor=0, patch=0, prerelease=None, build=None) (type: semver.version.Version)`
