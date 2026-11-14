# VerDiff Differential Analysis: `urllib3` (`2.0.2` -> `2.0.7`)

## 1. Executive Telemetry Summary

| Metric | Value |
| :--- | :--- |
| **Package** | `urllib3` |
| **Version A (Baseline)** | `2.0.2` |
| **Version B (Target)** | `2.0.7` |
| **Python Runtime** | `3.12.14` |
| **Deterministic Seed** | `42` |
| **Public Callables (`v1` / `v2`)** | `246` / `246` |
| **Unchanged Signatures** | `242` |
| **Static Signature Changes** | `4` |
| **Callables & Chains Fuzzed** | `120` |
| **Synthesized Inputs Executed** | `5413` |
| **Non-Breaking Object Noise Filtered** | `0` |
| **Max Drifts Ceiling (`--max-drifts`)** | `Unlimited (0)` |
| **Silent Behavioral Drifts Found** | **`9`** |
| **Wall-Clock Duration** | `9.55s` |

## 2. Static API Surface Changes (4)

| Change Kind | Module | Symbol (`v1` -> `v2`) | Signature / Details |
| :--- | :--- | :--- | :--- |
| `signature_changed` | `urllib3.connection` | `HTTPConnection` | parameter 'blocksize' default value changed (8192 -> 16384) |
| `signature_changed` | `urllib3.connection` | `HTTPSConnection` | parameter 'blocksize' default value changed (8192 -> 16384) |
| `signature_changed` | `urllib3.connection` | `VerifiedHTTPSConnection` | parameter 'blocksize' default value changed (8192 -> 16384) |
| `signature_changed` | `urllib3.util.retry` | `Retry` | parameter 'remove_headers_on_redirect' default value changed (frozenset({'Authorization'}) -> frozenset({'Authorization', 'Cookie'})) |

## 3. Discovered Behavioral Drifts (9)

### 3.1 `urllib3.connection.HTTPConnection(host: str, port: int | None = None, *, timeout: _TYPE_TIMEOUT = <_TYPE_DEFAULT.token: -1>, source_address: tuple[str, int] | None = None, blocksize: int = 8192, socket_options: None | connection._TYPE_SOCKET_OPTIONS = [(6, 1, 1)], proxy: Url | None = None, proxy_config: ProxyConfig | None = None) -> HTTPConnection`
- **Drift Category:** `return_value_drift` (`value_or_type_mismatch`)
- **Summary:** Return object state drift on <urllib3.connection.HTTPConnection object at 0xADDR> (urllib3.connection.HTTPConnection): attribute 'blocksize' changed (8192 -> 16384)
- **Input Strategy:** `edge_sweep_positional`
- **Original Fuzzed Call:** `HTTPConnection('https://example.com/path?a=1&b=2#sec', 0)`
- **Shrunk Minimal Call (1 shrink steps):** `HTTPConnection('', 0)`
- **Baseline (`2.0.2`):** `RETURN <urllib3.connection.HTTPConnection object at 0xADDR> (type: urllib3.connection.HTTPConnection)`
- **Target (`2.0.7`):** `RETURN <urllib3.connection.HTTPConnection object at 0xADDR> (type: urllib3.connection.HTTPConnection)`

### 3.2 `urllib3.connection.HTTPSConnection(host: str, port: int | None = None, *, timeout: _TYPE_TIMEOUT = <_TYPE_DEFAULT.token: -1>, source_address: tuple[str, int] | None = None, blocksize: int = 8192, socket_options: None | connection._TYPE_SOCKET_OPTIONS = [(6, 1, 1)], proxy: Url | None = None, proxy_config: ProxyConfig | None = None, cert_reqs: int | str | None = None, assert_hostname: None | str | Literal[False] = None, assert_fingerprint: str | None = None, server_hostname: str | None = None, ssl_context: ssl.SSLContext | None = None, ca_certs: str | None = None, ca_cert_dir: str | None = None, ca_cert_data: None | str | bytes = None, ssl_minimum_version: int | None = None, ssl_maximum_version: int | None = None, ssl_version: int | str | None = None, cert_file: str | None = None, key_file: str | None = None, key_password: str | None = None) -> HTTPSConnection`
- **Drift Category:** `return_value_drift` (`value_or_type_mismatch`)
- **Summary:** Return object state drift on <urllib3.connection.HTTPSConnection object at 0xADDR> (urllib3.connection.HTTPSConnection): attribute 'blocksize' changed (8192 -> 16384)
- **Input Strategy:** `edge_sweep_positional`
- **Original Fuzzed Call:** `HTTPSConnection('https://example.com/path?a=1&b=2#sec', 0)`
- **Shrunk Minimal Call (1 shrink steps):** `HTTPSConnection('', 0)`
- **Baseline (`2.0.2`):** `RETURN <urllib3.connection.HTTPSConnection object at 0xADDR> (type: urllib3.connection.HTTPSConnection)`
- **Target (`2.0.7`):** `RETURN <urllib3.connection.HTTPSConnection object at 0xADDR> (type: urllib3.connection.HTTPSConnection)`

### 3.3 `urllib3.connection.VerifiedHTTPSConnection(host: str, port: int | None = None, *, timeout: _TYPE_TIMEOUT = <_TYPE_DEFAULT.token: -1>, source_address: tuple[str, int] | None = None, blocksize: int = 8192, socket_options: None | connection._TYPE_SOCKET_OPTIONS = [(6, 1, 1)], proxy: Url | None = None, proxy_config: ProxyConfig | None = None, cert_reqs: int | str | None = None, assert_hostname: None | str | Literal[False] = None, assert_fingerprint: str | None = None, server_hostname: str | None = None, ssl_context: ssl.SSLContext | None = None, ca_certs: str | None = None, ca_cert_dir: str | None = None, ca_cert_data: None | str | bytes = None, ssl_minimum_version: int | None = None, ssl_maximum_version: int | None = None, ssl_version: int | str | None = None, cert_file: str | None = None, key_file: str | None = None, key_password: str | None = None) -> VerifiedHTTPSConnection`
- **Drift Category:** `return_value_drift` (`value_or_type_mismatch`)
- **Summary:** Return object state drift on <urllib3.connection.HTTPSConnection object at 0xADDR> (urllib3.connection.HTTPSConnection): attribute 'blocksize' changed (8192 -> 16384)
- **Input Strategy:** `edge_sweep_positional`
- **Original Fuzzed Call:** `VerifiedHTTPSConnection('https://example.com/path?a=1&b=2#sec', 0)`
- **Shrunk Minimal Call (1 shrink steps):** `VerifiedHTTPSConnection('', 0)`
- **Baseline (`2.0.2`):** `RETURN <urllib3.connection.HTTPSConnection object at 0xADDR> (type: urllib3.connection.HTTPSConnection)`
- **Target (`2.0.7`):** `RETURN <urllib3.connection.HTTPSConnection object at 0xADDR> (type: urllib3.connection.HTTPSConnection)`

### 3.4 `urllib3.connectionpool.HTTPConnectionPool(host: str, port: int | None = None, timeout: _TYPE_TIMEOUT | None = <_TYPE_DEFAULT.token: -1>, maxsize: int = 1, block: bool = False, headers: typing.Mapping[str, str] | None = None, retries: Retry | bool | int | None = None, _proxy: Url | None = None, _proxy_headers: typing.Mapping[str, str] | None = None, _proxy_config: ProxyConfig | None = None, **conn_kw: typing.Any) -> HTTPConnectionPool`
- **Drift Category:** `return_value_drift` (`value_or_type_mismatch`)
- **Summary:** Return object state drift on <urllib3.connectionpool.HTTPConnectionPool object at 0xADDR> (urllib3.connectionpool.HTTPConnectionPool): attribute 'retries.remove_headers_on_redirect' changed (frozenset(['authorization']) -> frozenset(['authorization', 'cookie']))
- **Input Strategy:** `baseline_required`
- **Original Fuzzed Call:** `HTTPConnectionPool('https://example.com/path?a=1&b=2#sec')`
- **Shrunk Minimal Call (5 shrink steps):** `HTTPConnectionPool('h')`
- **Baseline (`2.0.2`):** `RETURN <urllib3.connectionpool.HTTPConnectionPool object at 0xADDR> (type: urllib3.connectionpool.HTTPConnectionPool)`
- **Target (`2.0.7`):** `RETURN <urllib3.connectionpool.HTTPConnectionPool object at 0xADDR> (type: urllib3.connectionpool.HTTPConnectionPool)`

### 3.5 `urllib3.connectionpool.HTTPSConnectionPool(host: str, port: int | None = None, timeout: _TYPE_TIMEOUT | None = <_TYPE_DEFAULT.token: -1>, maxsize: int = 1, block: bool = False, headers: typing.Mapping[str, str] | None = None, retries: Retry | bool | int | None = None, _proxy: Url | None = None, _proxy_headers: typing.Mapping[str, str] | None = None, key_file: str | None = None, cert_file: str | None = None, cert_reqs: int | str | None = None, key_password: str | None = None, ca_certs: str | None = None, ssl_version: int | str | None = None, ssl_minimum_version: ssl.TLSVersion | None = None, ssl_maximum_version: ssl.TLSVersion | None = None, assert_hostname: str | Literal[False] | None = None, assert_fingerprint: str | None = None, ca_cert_dir: str | None = None, **conn_kw: typing.Any) -> HTTPSConnectionPool`
- **Drift Category:** `return_value_drift` (`value_or_type_mismatch`)
- **Summary:** Return object state drift on <urllib3.connectionpool.HTTPSConnectionPool object at 0xADDR> (urllib3.connectionpool.HTTPSConnectionPool): attribute 'retries.remove_headers_on_redirect' changed (frozenset(['authorization']) -> frozenset(['authorization', 'cookie']))
- **Input Strategy:** `baseline_required`
- **Original Fuzzed Call:** `HTTPSConnectionPool('https://example.com/path?a=1&b=2#sec')`
- **Shrunk Minimal Call (5 shrink steps):** `HTTPSConnectionPool('h')`
- **Baseline (`2.0.2`):** `RETURN <urllib3.connectionpool.HTTPSConnectionPool object at 0xADDR> (type: urllib3.connectionpool.HTTPSConnectionPool)`
- **Target (`2.0.7`):** `RETURN <urllib3.connectionpool.HTTPSConnectionPool object at 0xADDR> (type: urllib3.connectionpool.HTTPSConnectionPool)`

### 3.6 `urllib3.poolmanager.PoolManager.<stateful_chain>[stateful chain: clear, connection_from_context, connection_from_host, connection_from_pool_key]`
- **Drift Category:** `return_value_drift` (`value_or_type_mismatch`)
- **Summary:** Return object state drift on [<urllib3.connectionpool.HTTPConnectionPool object at 0xADDR>] (builtins.list): attribute '[0].retries.remove_headers_on_redirect' changed (frozenset(['authorization']) -> frozenset(['authorization', 'cookie']))
- **Input Strategy:** `stateful_call_chain`
- **Original Fuzzed Call:** `obj = PoolManager(); obj.clear(); obj.connection_from_host('a')`
- **Shrunk Minimal Call (1 shrink steps):** `obj = PoolManager(); obj.connection_from_host('a')`
- **Baseline (`2.0.2`):** `RETURN [<urllib3.connectionpool.HTTPConnectionPool object at 0xADDR>] (type: builtins.list)`
- **Target (`2.0.7`):** `RETURN [<urllib3.connectionpool.HTTPConnectionPool object at 0xADDR>] (type: builtins.list)`

### 3.7 `urllib3.poolmanager.ProxyManager.<stateful_chain>[stateful chain: clear, connection_from_context, connection_from_host, connection_from_pool_key]`
- **Drift Category:** `return_value_drift` (`value_or_type_mismatch`)
- **Summary:** Return object state drift on [<urllib3.connectionpool.HTTPSConnectionPool object at 0xADDR>] (builtins.list): attribute '[0].retries.remove_headers_on_redirect' changed (frozenset(['authorization']) -> frozenset(['authorization', 'cookie']))
- **Input Strategy:** `stateful_call_chain`
- **Original Fuzzed Call:** `obj = ProxyManager('https://example.com/path?a=1&b=2#sec'); obj.clear(); obj.connection_from_host('a')`
- **Shrunk Minimal Call (2 shrink steps):** `obj = ProxyManager('https://example.com/path?a=1&b=2#sec'); obj.connection_from_host('')`
- **Baseline (`2.0.2`):** `RETURN [<urllib3.connectionpool.HTTPSConnectionPool object at 0xADDR>] (type: builtins.list)`
- **Target (`2.0.7`):** `RETURN [<urllib3.connectionpool.HTTPSConnectionPool object at 0xADDR>] (type: builtins.list)`

### 3.8 `urllib3.util.retry.Retry(total: bool | int | None = 10, connect: int | None = None, read: int | None = None, redirect: bool | int | None = None, status: int | None = None, other: int | None = None, allowed_methods: typing.Collection[str] | None = frozenset({'GET', 'DELETE', 'PUT', 'HEAD', 'TRACE', 'OPTIONS'}), status_forcelist: typing.Collection[int] | None = None, backoff_factor: float = 0, backoff_max: float = 120, raise_on_redirect: bool = True, raise_on_status: bool = True, history: tuple[RequestHistory, ...] | None = None, respect_retry_after_header: bool = True, remove_headers_on_redirect: typing.Collection[str] = frozenset({'Authorization'}), backoff_jitter: float = 0.0) -> Retry`
- **Drift Category:** `return_value_drift` (`value_or_type_mismatch`)
- **Summary:** Return object state drift on Retry(total=10, connect=None, read=None, redirect=None, status=None) (urllib3.util.retry.Retry): attribute 'remove_headers_on_redirect' changed (frozenset(['authorization']) -> frozenset(['authorization', 'cookie']))
- **Input Strategy:** `defaults_only`
- **Original Fuzzed Call:** `Retry()`
- **Shrunk Minimal Call (0 shrink steps):** `Retry()`
- **Baseline (`2.0.2`):** `RETURN Retry(total=10, connect=None, read=None, redirect=None, status=None) (type: urllib3.util.retry.Retry)`
- **Target (`2.0.7`):** `RETURN Retry(total=10, connect=None, read=None, redirect=None, status=None) (type: urllib3.util.retry.Retry)`

### 3.9 `urllib3.util.retry.Retry.<stateful_chain>[stateful chain: get_backoff_time, get_retry_after, increment, is_exhausted]`
- **Drift Category:** `return_value_drift` (`value_or_type_mismatch`)
- **Summary:** Return object state drift on [Retry(total=9, connect=None, read=None, redirect=None, status=None)] (builtins.list): attribute '[0].remove_headers_on_redirect' changed (frozenset(['authorization']) -> frozenset(['authorization', 'cookie']))
- **Input Strategy:** `stateful_call_chain`
- **Original Fuzzed Call:** `obj = Retry(); obj.get_backoff_time(); obj.increment()`
- **Shrunk Minimal Call (1 shrink steps):** `obj = Retry(); obj.increment()`
- **Baseline (`2.0.2`):** `RETURN [Retry(total=9, connect=None, read=None, redirect=None, status=None)] (type: builtins.list)`
- **Target (`2.0.7`):** `RETURN [Retry(total=9, connect=None, read=None, redirect=None, status=None)] (type: builtins.list)`
