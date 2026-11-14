# VerDiff Differential Analysis: `urllib3` (`1.26.18` -> `2.0.7`)

## 1. Executive Telemetry Summary

| Metric | Value |
| :--- | :--- |
| **Package** | `urllib3` |
| **Version A (Baseline)** | `1.26.18` |
| **Version B (Target)** | `2.0.7` |
| **Python Runtime** | `3.12.14` |
| **Deterministic Seed** | `42` |
| **Public Callables (`v1` / `v2`)** | `268` / `246` |
| **Unchanged Signatures** | `30` |
| **Static Signature Changes** | `238` |
| **Callables & Chains Fuzzed** | `120` |
| **Synthesized Inputs Executed** | `6971` |
| **Non-Breaking Object Noise Filtered** | `161` |
| **Max Drifts Ceiling (`--max-drifts`)** | `Unlimited (0)` |
| **Silent Behavioral Drifts Found** | **`35`** |
| **Wall-Clock Duration** | `13.12s` |

## 2. Static API Surface Changes (274)

| Change Kind | Module | Symbol (`v1` -> `v2`) | Signature / Details |
| :--- | :--- | :--- | :--- |
| `signature_changed` | `urllib3` | `add_stderr_logger` | parameter 'level' type annotation changed (untyped -> int); return annotation changed (untyped -> logging.StreamHandler[typing.TextIO]) |
| `signature_changed` | `urllib3` | `disable_warnings` | parameter 'category' type annotation changed (untyped -> type[Warning]); return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.connection` | `HTTPConnection` | parameter count changed (2 -> 8) |
| `signature_changed` | `urllib3.connection` | `HTTPConnection.close` | return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.connection` | `HTTPConnection.connect` | return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.connection` | `HTTPConnection.getresponse` | return annotation changed (untyped -> HTTPResponse) |
| `signature_changed` | `urllib3.connection` | `HTTPConnection.putheader` | parameter 'header' type annotation changed (untyped -> str); parameter 'values' type annotation changed (untyped -> str); return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.connection` | `HTTPConnection.putrequest` | parameter 'method' type annotation changed (untyped -> str); parameter 'url' type annotation changed (untyped -> str); parameter 'args' renamed to 'skip_host'; parameter 'args' kind changed (VAR_POSITIONAL -> POSITIONAL_OR_KEYWORD); parameter 'args' default added; parameter 'args' type annotation changed (untyped -> bool); parameter 'kwargs' renamed to 'skip_accept_encoding'; parameter 'kwargs' kind changed (VAR_KEYWORD -> POSITIONAL_OR_KEYWORD); parameter 'kwargs' default added; parameter 'kwargs' type annotation changed (untyped -> bool); return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.connection` | `HTTPConnection.request` | parameter count changed (4 -> 8); return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.connection` | `HTTPConnection.request_chunked` | parameter 'method' type annotation changed (untyped -> str); parameter 'url' type annotation changed (untyped -> str); parameter 'body' type annotation changed (untyped -> _TYPE_BODY | None); parameter 'headers' type annotation changed (untyped -> typing.Mapping[str, str] | None); return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.connection` | `HTTPConnection.set_tunnel` | parameter count changed (3 -> 4); return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.connection` | `HTTPHeaderDict` | parameter 'headers' type annotation changed (untyped -> ValidHTTPHeaderSource | None); parameter 'kwargs' type annotation changed (untyped -> str) |
| `signature_changed` | `urllib3.connection` | `HTTPHeaderDict.add` | parameter count changed (2 -> 3); return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.connection` | `HTTPHeaderDict.copy` | return annotation changed (untyped -> HTTPHeaderDict) |
| `signature_changed` | `urllib3.connection` | `HTTPHeaderDict.discard` | parameter 'key' type annotation changed (untyped -> str); return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.connection` | `HTTPHeaderDict.extend` | parameter 'args' type annotation changed (untyped -> ValidHTTPHeaderSource); parameter 'kwargs' type annotation changed (untyped -> str); return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.connection` | `HTTPHeaderDict.get_all` | parameter 'key' type annotation changed (untyped -> str); parameter 'default' default value changed (<object object at 0xADDR> -> <_Sentinel.not_passed: 1>); parameter 'default' type annotation changed (untyped -> _Sentinel | _DT); return annotation changed (untyped -> list[str] | _DT) |
| `signature_changed` | `urllib3.connection` | `HTTPHeaderDict.getallmatchingheaders` | parameter 'key' type annotation changed (untyped -> str); parameter 'default' default value changed (<object object at 0xADDR> -> <_Sentinel.not_passed: 1>); parameter 'default' type annotation changed (untyped -> _Sentinel | _DT); return annotation changed (untyped -> list[str] | _DT) |
| `signature_changed` | `urllib3.connection` | `HTTPHeaderDict.getheaders` | parameter 'key' type annotation changed (untyped -> str); parameter 'default' default value changed (<object object at 0xADDR> -> <_Sentinel.not_passed: 1>); parameter 'default' type annotation changed (untyped -> _Sentinel | _DT); return annotation changed (untyped -> list[str] | _DT) |
| `signature_changed` | `urllib3.connection` | `HTTPHeaderDict.getlist` | parameter 'key' type annotation changed (untyped -> str); parameter 'default' default value changed (<object object at 0xADDR> -> <_Sentinel.not_passed: 1>); parameter 'default' type annotation changed (untyped -> _Sentinel | _DT); return annotation changed (untyped -> list[str] | _DT) |
| `signature_changed` | `urllib3.connection` | `HTTPHeaderDict.iget` | parameter 'key' type annotation changed (untyped -> str); parameter 'default' default value changed (<object object at 0xADDR> -> <_Sentinel.not_passed: 1>); parameter 'default' type annotation changed (untyped -> _Sentinel | _DT); return annotation changed (untyped -> list[str] | _DT) |
| `signature_changed` | `urllib3.connection` | `HTTPHeaderDict.items` | return annotation changed (untyped -> HTTPHeaderDictItemView) |
| `signature_changed` | `urllib3.connection` | `HTTPHeaderDict.iteritems` | return annotation changed (untyped -> typing.Iterator[tuple[str, str]]) |
| `signature_changed` | `urllib3.connection` | `HTTPHeaderDict.itermerged` | return annotation changed (untyped -> typing.Iterator[tuple[str, str]]) |
| `signature_changed` | `urllib3.connection` | `HTTPHeaderDict.setdefault` | parameter 'key' type annotation changed (untyped -> str); parameter 'default' default value changed (None -> ''); parameter 'default' type annotation changed (untyped -> str); return annotation changed (untyped -> str) |
| `signature_changed` | `urllib3.connection` | `HTTPSConnection` | parameter count changed (10 -> 22) |
| `signature_changed` | `urllib3.connection` | `HTTPSConnection.close` | return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.connection` | `HTTPSConnection.connect` | return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.connection` | `HTTPSConnection.getresponse` | return annotation changed (untyped -> HTTPResponse) |
| `signature_changed` | `urllib3.connection` | `HTTPSConnection.putheader` | parameter 'header' type annotation changed (untyped -> str); parameter 'values' type annotation changed (untyped -> str); return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.connection` | `HTTPSConnection.putrequest` | parameter 'method' type annotation changed (untyped -> str); parameter 'url' type annotation changed (untyped -> str); parameter 'args' renamed to 'skip_host'; parameter 'args' kind changed (VAR_POSITIONAL -> POSITIONAL_OR_KEYWORD); parameter 'args' default added; parameter 'args' type annotation changed (untyped -> bool); parameter 'kwargs' renamed to 'skip_accept_encoding'; parameter 'kwargs' kind changed (VAR_KEYWORD -> POSITIONAL_OR_KEYWORD); parameter 'kwargs' default added; parameter 'kwargs' type annotation changed (untyped -> bool); return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.connection` | `HTTPSConnection.request` | parameter count changed (4 -> 8); return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.connection` | `HTTPSConnection.request_chunked` | parameter 'method' type annotation changed (untyped -> str); parameter 'url' type annotation changed (untyped -> str); parameter 'body' type annotation changed (untyped -> _TYPE_BODY | None); parameter 'headers' type annotation changed (untyped -> typing.Mapping[str, str] | None); return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.connection` | `HTTPSConnection.set_cert` | parameter 'key_file' type annotation changed (untyped -> str | None); parameter 'cert_file' type annotation changed (untyped -> str | None); parameter 'cert_reqs' type annotation changed (untyped -> int | str | None); parameter 'key_password' type annotation changed (untyped -> str | None); parameter 'ca_certs' type annotation changed (untyped -> str | None); parameter 'assert_hostname' type annotation changed (untyped -> None | str | Literal[False]); parameter 'assert_fingerprint' type annotation changed (untyped -> str | None); parameter 'ca_cert_dir' type annotation changed (untyped -> str | None); parameter 'ca_cert_data' type annotation changed (untyped -> None | str | bytes); return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.connection` | `HTTPSConnection.set_tunnel` | parameter count changed (3 -> 4); return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.connection` | `VerifiedHTTPSConnection` | parameter count changed (10 -> 22) |
| `signature_changed` | `urllib3.connection` | `VerifiedHTTPSConnection.close` | return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.connection` | `VerifiedHTTPSConnection.connect` | return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.connection` | `VerifiedHTTPSConnection.getresponse` | return annotation changed (untyped -> HTTPResponse) |
| `signature_changed` | `urllib3.connection` | `VerifiedHTTPSConnection.putheader` | parameter 'header' type annotation changed (untyped -> str); parameter 'values' type annotation changed (untyped -> str); return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.connection` | `VerifiedHTTPSConnection.putrequest` | parameter 'method' type annotation changed (untyped -> str); parameter 'url' type annotation changed (untyped -> str); parameter 'args' renamed to 'skip_host'; parameter 'args' kind changed (VAR_POSITIONAL -> POSITIONAL_OR_KEYWORD); parameter 'args' default added; parameter 'args' type annotation changed (untyped -> bool); parameter 'kwargs' renamed to 'skip_accept_encoding'; parameter 'kwargs' kind changed (VAR_KEYWORD -> POSITIONAL_OR_KEYWORD); parameter 'kwargs' default added; parameter 'kwargs' type annotation changed (untyped -> bool); return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.connection` | `VerifiedHTTPSConnection.request` | parameter count changed (4 -> 8); return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.connection` | `VerifiedHTTPSConnection.request_chunked` | parameter 'method' type annotation changed (untyped -> str); parameter 'url' type annotation changed (untyped -> str); parameter 'body' type annotation changed (untyped -> _TYPE_BODY | None); parameter 'headers' type annotation changed (untyped -> typing.Mapping[str, str] | None); return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.connection` | `VerifiedHTTPSConnection.set_cert` | parameter 'key_file' type annotation changed (untyped -> str | None); parameter 'cert_file' type annotation changed (untyped -> str | None); parameter 'cert_reqs' type annotation changed (untyped -> int | str | None); parameter 'key_password' type annotation changed (untyped -> str | None); parameter 'ca_certs' type annotation changed (untyped -> str | None); parameter 'assert_hostname' type annotation changed (untyped -> None | str | Literal[False]); parameter 'assert_fingerprint' type annotation changed (untyped -> str | None); parameter 'ca_cert_dir' type annotation changed (untyped -> str | None); parameter 'ca_cert_data' type annotation changed (untyped -> None | str | bytes); return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.connection` | `VerifiedHTTPSConnection.set_tunnel` | parameter count changed (3 -> 4); return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.connectionpool` | `ConnectionPool` | parameter 'host' type annotation changed (untyped -> str); parameter 'port' type annotation changed (untyped -> int | None) |
| `signature_changed` | `urllib3.connectionpool` | `ConnectionPool.close` | return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.connectionpool` | `HTTPConnectionPool` | parameter count changed (12 -> 11) |
| `signature_changed` | `urllib3.connectionpool` | `HTTPConnectionPool.close` | return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.connectionpool` | `HTTPConnectionPool.is_same_host` | parameter 'url' type annotation changed (untyped -> str); return annotation changed (untyped -> bool) |
| `signature_changed` | `urllib3.connectionpool` | `HTTPConnectionPool.request` | parameter count changed (5 -> 7); return annotation changed (untyped -> BaseHTTPResponse) |
| `signature_changed` | `urllib3.connectionpool` | `HTTPConnectionPool.request_encode_body` | parameter 'method' type annotation changed (untyped -> str); parameter 'url' type annotation changed (untyped -> str); parameter 'fields' type annotation changed (untyped -> _TYPE_FIELDS | None); parameter 'headers' type annotation changed (untyped -> typing.Mapping[str, str] | None); parameter 'encode_multipart' type annotation changed (untyped -> bool); parameter 'multipart_boundary' type annotation changed (untyped -> str | None); parameter 'urlopen_kw' type annotation changed (untyped -> str); return annotation changed (untyped -> BaseHTTPResponse) |
| `signature_changed` | `urllib3.connectionpool` | `HTTPConnectionPool.request_encode_url` | parameter 'method' type annotation changed (untyped -> str); parameter 'url' type annotation changed (untyped -> str); parameter 'fields' type annotation changed (untyped -> _TYPE_ENCODE_URL_FIELDS | None); parameter 'headers' type annotation changed (untyped -> typing.Mapping[str, str] | None); parameter 'urlopen_kw' type annotation changed (untyped -> str); return annotation changed (untyped -> BaseHTTPResponse) |
| `signature_changed` | `urllib3.connectionpool` | `HTTPConnectionPool.urlopen` | parameter count changed (13 -> 15); return annotation changed (untyped -> BaseHTTPResponse) |
| `signature_changed` | `urllib3.connectionpool` | `HTTPSConnectionPool` | parameter count changed (20 -> 21) |
| `signature_changed` | `urllib3.connectionpool` | `HTTPSConnectionPool.close` | return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.connectionpool` | `HTTPSConnectionPool.is_same_host` | parameter 'url' type annotation changed (untyped -> str); return annotation changed (untyped -> bool) |
| `signature_changed` | `urllib3.connectionpool` | `HTTPSConnectionPool.request` | parameter count changed (5 -> 7); return annotation changed (untyped -> BaseHTTPResponse) |
| `signature_changed` | `urllib3.connectionpool` | `HTTPSConnectionPool.request_encode_body` | parameter 'method' type annotation changed (untyped -> str); parameter 'url' type annotation changed (untyped -> str); parameter 'fields' type annotation changed (untyped -> _TYPE_FIELDS | None); parameter 'headers' type annotation changed (untyped -> typing.Mapping[str, str] | None); parameter 'encode_multipart' type annotation changed (untyped -> bool); parameter 'multipart_boundary' type annotation changed (untyped -> str | None); parameter 'urlopen_kw' type annotation changed (untyped -> str); return annotation changed (untyped -> BaseHTTPResponse) |
| `signature_changed` | `urllib3.connectionpool` | `HTTPSConnectionPool.request_encode_url` | parameter 'method' type annotation changed (untyped -> str); parameter 'url' type annotation changed (untyped -> str); parameter 'fields' type annotation changed (untyped -> _TYPE_ENCODE_URL_FIELDS | None); parameter 'headers' type annotation changed (untyped -> typing.Mapping[str, str] | None); parameter 'urlopen_kw' type annotation changed (untyped -> str); return annotation changed (untyped -> BaseHTTPResponse) |
| `signature_changed` | `urllib3.connectionpool` | `HTTPSConnectionPool.urlopen` | parameter count changed (13 -> 15); return annotation changed (untyped -> BaseHTTPResponse) |
| `signature_changed` | `urllib3.connectionpool` | `connection_from_url` | parameter 'url' type annotation changed (untyped -> str); parameter 'kw' type annotation changed (untyped -> typing.Any); return annotation changed (untyped -> HTTPConnectionPool) |
| `signature_changed` | `urllib3.fields` | `RequestField` | parameter 'name' type annotation changed (untyped -> str); parameter 'data' type annotation changed (untyped -> _TYPE_FIELD_VALUE); parameter 'filename' type annotation changed (untyped -> str | None); parameter 'headers' type annotation changed (untyped -> typing.Mapping[str, str] | None); parameter 'header_formatter' default value changed (<function format_header_param_html5 at 0xADDR> -> None); parameter 'header_formatter' type annotation changed (untyped -> typing.Callable[[str, _TYPE_FIELD_VALUE], str] | None) |
| `signature_changed` | `urllib3.fields` | `RequestField.from_tuples` | parameter 'fieldname' type annotation changed (untyped -> str); parameter 'value' type annotation changed (untyped -> _TYPE_FIELD_VALUE_TUPLE); parameter 'header_formatter' default value changed (<function format_header_param_html5 at 0xADDR> -> None); parameter 'header_formatter' type annotation changed (untyped -> typing.Callable[[str, _TYPE_FIELD_VALUE], str] | None); return annotation changed (untyped -> RequestField) |
| `signature_changed` | `urllib3.fields` | `RequestField.make_multipart` | parameter 'content_disposition' type annotation changed (untyped -> str | None); parameter 'content_type' type annotation changed (untyped -> str | None); parameter 'content_location' type annotation changed (untyped -> str | None); return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.fields` | `RequestField.render_headers` | return annotation changed (untyped -> str) |
| `signature_changed` | `urllib3.fields` | `format_header_param` | parameter 'name' type annotation changed (untyped -> str); parameter 'value' type annotation changed (untyped -> _TYPE_FIELD_VALUE); return annotation changed (untyped -> str) |
| `signature_changed` | `urllib3.fields` | `format_header_param_html5` | parameter 'name' type annotation changed (untyped -> str); parameter 'value' type annotation changed (untyped -> _TYPE_FIELD_VALUE); return annotation changed (untyped -> str) |
| `signature_changed` | `urllib3.fields` | `format_header_param_rfc2231` | parameter 'name' type annotation changed (untyped -> str); parameter 'value' type annotation changed (untyped -> _TYPE_FIELD_VALUE); return annotation changed (untyped -> str) |
| `signature_changed` | `urllib3.fields` | `guess_content_type` | parameter 'filename' type annotation changed (untyped -> str | None); parameter 'default' type annotation changed (untyped -> str); return annotation changed (untyped -> str) |
| `signature_changed` | `urllib3.filepost` | `choose_boundary` | return annotation changed (untyped -> str) |
| `signature_changed` | `urllib3.filepost` | `encode_multipart_formdata` | parameter 'fields' type annotation changed (untyped -> _TYPE_FIELDS); parameter 'boundary' type annotation changed (untyped -> str | None); return annotation changed (untyped -> tuple[bytes, str]) |
| `signature_changed` | `urllib3.filepost` | `iter_field_objects` | parameter 'fields' type annotation changed (untyped -> _TYPE_FIELDS); return annotation changed (untyped -> typing.Iterable[RequestField]) |
| `signature_changed` | `urllib3.poolmanager` | `PoolKey` | parameter count changed (26 -> 28) |
| `signature_changed` | `urllib3.poolmanager` | `PoolManager` | parameter 'num_pools' type annotation changed (untyped -> int); parameter 'headers' type annotation changed (untyped -> typing.Mapping[str, str] | None); parameter 'connection_pool_kw' type annotation changed (untyped -> typing.Any) |
| `signature_changed` | `urllib3.poolmanager` | `PoolManager.clear` | return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.poolmanager` | `PoolManager.connection_from_context` | parameter 'request_context' type annotation changed (untyped -> dict[str, typing.Any]); return annotation changed (untyped -> HTTPConnectionPool) |
| `signature_changed` | `urllib3.poolmanager` | `PoolManager.connection_from_host` | parameter 'host' type annotation changed (untyped -> str | None); parameter 'port' type annotation changed (untyped -> int | None); parameter 'scheme' type annotation changed (untyped -> str | None); parameter 'pool_kwargs' type annotation changed (untyped -> dict[str, typing.Any] | None); return annotation changed (untyped -> HTTPConnectionPool) |
| `signature_changed` | `urllib3.poolmanager` | `PoolManager.connection_from_pool_key` | parameter 'pool_key' type annotation changed (untyped -> PoolKey); parameter 'request_context' default removed; parameter 'request_context' type annotation changed (untyped -> dict[str, typing.Any]); return annotation changed (untyped -> HTTPConnectionPool) |
| `signature_changed` | `urllib3.poolmanager` | `PoolManager.connection_from_url` | parameter 'url' type annotation changed (untyped -> str); parameter 'pool_kwargs' type annotation changed (untyped -> dict[str, typing.Any] | None); return annotation changed (untyped -> HTTPConnectionPool) |
| `signature_changed` | `urllib3.poolmanager` | `PoolManager.request` | parameter count changed (5 -> 7); return annotation changed (untyped -> BaseHTTPResponse) |
| `signature_changed` | `urllib3.poolmanager` | `PoolManager.request_encode_body` | parameter 'method' type annotation changed (untyped -> str); parameter 'url' type annotation changed (untyped -> str); parameter 'fields' type annotation changed (untyped -> _TYPE_FIELDS | None); parameter 'headers' type annotation changed (untyped -> typing.Mapping[str, str] | None); parameter 'encode_multipart' type annotation changed (untyped -> bool); parameter 'multipart_boundary' type annotation changed (untyped -> str | None); parameter 'urlopen_kw' type annotation changed (untyped -> str); return annotation changed (untyped -> BaseHTTPResponse) |
| `signature_changed` | `urllib3.poolmanager` | `PoolManager.request_encode_url` | parameter 'method' type annotation changed (untyped -> str); parameter 'url' type annotation changed (untyped -> str); parameter 'fields' type annotation changed (untyped -> _TYPE_ENCODE_URL_FIELDS | None); parameter 'headers' type annotation changed (untyped -> typing.Mapping[str, str] | None); parameter 'urlopen_kw' type annotation changed (untyped -> str); return annotation changed (untyped -> BaseHTTPResponse) |
| `signature_changed` | `urllib3.poolmanager` | `PoolManager.urlopen` | parameter 'method' type annotation changed (untyped -> str); parameter 'url' type annotation changed (untyped -> str); parameter 'redirect' type annotation changed (untyped -> bool); parameter 'kw' type annotation changed (untyped -> typing.Any); return annotation changed (untyped -> BaseHTTPResponse) |
| `signature_changed` | `urllib3.poolmanager` | `ProxyManager` | parameter count changed (7 -> 9) |
| `signature_changed` | `urllib3.poolmanager` | `ProxyManager.clear` | return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.poolmanager` | `ProxyManager.connection_from_context` | parameter 'request_context' type annotation changed (untyped -> dict[str, typing.Any]); return annotation changed (untyped -> HTTPConnectionPool) |
| `signature_changed` | `urllib3.poolmanager` | `ProxyManager.connection_from_host` | parameter 'host' type annotation changed (untyped -> str | None); parameter 'port' type annotation changed (untyped -> int | None); parameter 'scheme' type annotation changed (untyped -> str | None); parameter 'pool_kwargs' type annotation changed (untyped -> dict[str, typing.Any] | None); return annotation changed (untyped -> HTTPConnectionPool) |
| `signature_changed` | `urllib3.poolmanager` | `ProxyManager.connection_from_pool_key` | parameter 'pool_key' type annotation changed (untyped -> PoolKey); parameter 'request_context' default removed; parameter 'request_context' type annotation changed (untyped -> dict[str, typing.Any]); return annotation changed (untyped -> HTTPConnectionPool) |
| `signature_changed` | `urllib3.poolmanager` | `ProxyManager.connection_from_url` | parameter 'url' type annotation changed (untyped -> str); parameter 'pool_kwargs' type annotation changed (untyped -> dict[str, typing.Any] | None); return annotation changed (untyped -> HTTPConnectionPool) |
| `signature_changed` | `urllib3.poolmanager` | `ProxyManager.request` | parameter count changed (5 -> 7); return annotation changed (untyped -> BaseHTTPResponse) |
| `signature_changed` | `urllib3.poolmanager` | `ProxyManager.request_encode_body` | parameter 'method' type annotation changed (untyped -> str); parameter 'url' type annotation changed (untyped -> str); parameter 'fields' type annotation changed (untyped -> _TYPE_FIELDS | None); parameter 'headers' type annotation changed (untyped -> typing.Mapping[str, str] | None); parameter 'encode_multipart' type annotation changed (untyped -> bool); parameter 'multipart_boundary' type annotation changed (untyped -> str | None); parameter 'urlopen_kw' type annotation changed (untyped -> str); return annotation changed (untyped -> BaseHTTPResponse) |
| `signature_changed` | `urllib3.poolmanager` | `ProxyManager.request_encode_url` | parameter 'method' type annotation changed (untyped -> str); parameter 'url' type annotation changed (untyped -> str); parameter 'fields' type annotation changed (untyped -> _TYPE_ENCODE_URL_FIELDS | None); parameter 'headers' type annotation changed (untyped -> typing.Mapping[str, str] | None); parameter 'urlopen_kw' type annotation changed (untyped -> str); return annotation changed (untyped -> BaseHTTPResponse) |
| `signature_changed` | `urllib3.poolmanager` | `ProxyManager.urlopen` | parameter 'method' type annotation changed (untyped -> str); parameter 'url' type annotation changed (untyped -> str); parameter 'redirect' type annotation changed (untyped -> bool); parameter 'kw' type annotation changed (untyped -> typing.Any); return annotation changed (untyped -> BaseHTTPResponse) |
| `signature_changed` | `urllib3.poolmanager` | `proxy_from_url` | parameter 'url' type annotation changed (untyped -> str); parameter 'kw' type annotation changed (untyped -> typing.Any); return annotation changed (untyped -> ProxyManager) |
| `signature_changed` | `urllib3.response` | `DeflateDecoder.decompress` | parameter 'data' type annotation changed (untyped -> bytes); return annotation changed (untyped -> bytes) |
| `signature_changed` | `urllib3.response` | `GzipDecoder.decompress` | parameter 'data' type annotation changed (untyped -> bytes); return annotation changed (untyped -> bytes) |
| `signature_changed` | `urllib3.response` | `HTTPResponse` | parameter count changed (17 -> 16) |
| `signature_changed` | `urllib3.response` | `HTTPResponse.close` | return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.response` | `HTTPResponse.drain_conn` | return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.response` | `HTTPResponse.fileno` | return annotation changed (untyped -> int) |
| `signature_changed` | `urllib3.response` | `HTTPResponse.flush` | return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.response` | `HTTPResponse.get_redirect_location` | return annotation changed (untyped -> str | None | Literal[False]) |
| `signature_changed` | `urllib3.response` | `HTTPResponse.getheader` | parameter 'name' type annotation changed (untyped -> str); parameter 'default' type annotation changed (untyped -> str | None); return annotation changed (untyped -> str | None) |
| `signature_changed` | `urllib3.response` | `HTTPResponse.getheaders` | return annotation changed (untyped -> HTTPHeaderDict) |
| `signature_changed` | `urllib3.response` | `HTTPResponse.geturl` | return annotation changed (untyped -> str | None) |
| `signature_changed` | `urllib3.response` | `HTTPResponse.info` | return annotation changed (untyped -> HTTPHeaderDict) |
| `signature_changed` | `urllib3.response` | `HTTPResponse.isclosed` | return annotation changed (untyped -> bool) |
| `signature_changed` | `urllib3.response` | `HTTPResponse.read` | parameter 'amt' type annotation changed (untyped -> int | None); parameter 'decode_content' type annotation changed (untyped -> bool | None); parameter 'cache_content' type annotation changed (untyped -> bool); return annotation changed (untyped -> bytes) |
| `signature_changed` | `urllib3.response` | `HTTPResponse.read_chunked` | parameter 'amt' type annotation changed (untyped -> int | None); parameter 'decode_content' type annotation changed (untyped -> bool | None); return annotation changed (untyped -> typing.Generator[bytes, None, None]) |
| `signature_changed` | `urllib3.response` | `HTTPResponse.readable` | return annotation changed (untyped -> bool) |
| `signature_changed` | `urllib3.response` | `HTTPResponse.readinto` | parameter 'b' type annotation changed (untyped -> bytearray); return annotation changed (untyped -> int) |
| `signature_changed` | `urllib3.response` | `HTTPResponse.release_conn` | return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.response` | `HTTPResponse.stream` | parameter 'amt' type annotation changed (untyped -> int | None); parameter 'decode_content' type annotation changed (untyped -> bool | None); return annotation changed (untyped -> typing.Generator[bytes, None, None]) |
| `signature_changed` | `urllib3.response` | `HTTPResponse.supports_chunked_reads` | return annotation changed (untyped -> bool) |
| `signature_changed` | `urllib3.response` | `HTTPResponse.tell` | return annotation changed (untyped -> int) |
| `signature_changed` | `urllib3.response` | `MultiDecoder` | parameter 'modes' type annotation changed (untyped -> str) |
| `signature_changed` | `urllib3.response` | `MultiDecoder.decompress` | parameter 'data' type annotation changed (untyped -> bytes); return annotation changed (untyped -> bytes) |
| `signature_changed` | `urllib3.response` | `MultiDecoder.flush` | return annotation changed (untyped -> bytes) |
| `signature_changed` | `urllib3.util.connection` | `allowed_gai_family` | return annotation changed (untyped -> socket.AddressFamily) |
| `signature_changed` | `urllib3.util.connection` | `create_connection` | parameter 'address' type annotation changed (untyped -> tuple[str, int]); parameter 'timeout' default value changed (<object object at 0xADDR> -> <_TYPE_DEFAULT.token: -1>); parameter 'timeout' type annotation changed (untyped -> _TYPE_TIMEOUT); parameter 'source_address' type annotation changed (untyped -> tuple[str, int] | None); parameter 'socket_options' type annotation changed (untyped -> _TYPE_SOCKET_OPTIONS | None); return annotation changed (untyped -> socket.socket) |
| `signature_changed` | `urllib3.util.connection` | `is_connection_dropped` | parameter 'conn' type annotation changed (untyped -> BaseHTTPConnection); return annotation changed (untyped -> bool) |
| `signature_changed` | `urllib3.util.proxy` | `connection_requires_http_tunnel` | parameter 'proxy_url' type annotation changed (untyped -> Url | None); parameter 'proxy_config' type annotation changed (untyped -> ProxyConfig | None); parameter 'destination_scheme' type annotation changed (untyped -> str | None); return annotation changed (untyped -> bool) |
| `signature_changed` | `urllib3.util.request` | `make_headers` | parameter 'keep_alive' type annotation changed (untyped -> bool | None); parameter 'accept_encoding' type annotation changed (untyped -> bool | list[str] | str | None); parameter 'user_agent' type annotation changed (untyped -> str | None); parameter 'basic_auth' type annotation changed (untyped -> str | None); parameter 'proxy_basic_auth' type annotation changed (untyped -> str | None); parameter 'disable_cache' type annotation changed (untyped -> bool | None); return annotation changed (untyped -> dict[str, str]) |
| `signature_changed` | `urllib3.util.request` | `rewind_body` | parameter 'body' type annotation changed (untyped -> typing.IO[typing.AnyStr]); parameter 'body_pos' type annotation changed (untyped -> _TYPE_BODY_POSITION); return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.util.request` | `set_file_position` | parameter 'body' type annotation changed (untyped -> typing.Any); parameter 'pos' type annotation changed (untyped -> _TYPE_BODY_POSITION | None); return annotation changed (untyped -> _TYPE_BODY_POSITION | None) |
| `signature_changed` | `urllib3.util.response` | `assert_header_parsing` | parameter 'headers' type annotation changed (untyped -> httplib.HTTPMessage); return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.util.response` | `is_fp_closed` | parameter 'obj' type annotation changed (untyped -> object); return annotation changed (untyped -> bool) |
| `signature_changed` | `urllib3.util.response` | `is_response_to_head` | parameter 'response' type annotation changed (untyped -> httplib.HTTPResponse); return annotation changed (untyped -> bool) |
| `signature_changed` | `urllib3.util.retry` | `RequestHistory` | parameter 'method' type annotation changed (untyped -> ForwardRef('str | None')); parameter 'url' type annotation changed (untyped -> ForwardRef('str | None')); parameter 'error' type annotation changed (untyped -> ForwardRef('Exception | None')); parameter 'status' type annotation changed (untyped -> ForwardRef('int | None')); parameter 'redirect_location' type annotation changed (untyped -> ForwardRef('str | None')) |
| `signature_changed` | `urllib3.util.retry` | `Retry` | parameter count changed (15 -> 16) |
| `signature_changed` | `urllib3.util.retry` | `Retry.from_int` | parameter 'retries' type annotation changed (untyped -> Retry | bool | int | None); parameter 'redirect' type annotation changed (untyped -> bool | int | None); parameter 'default' type annotation changed (untyped -> Retry | bool | int | None); return annotation changed (untyped -> Retry) |
| `signature_changed` | `urllib3.util.retry` | `Retry.get_backoff_time` | return annotation changed (untyped -> float) |
| `signature_changed` | `urllib3.util.retry` | `Retry.get_retry_after` | parameter 'response' type annotation changed (untyped -> BaseHTTPResponse); return annotation changed (untyped -> float | None) |
| `signature_changed` | `urllib3.util.retry` | `Retry.increment` | parameter 'method' type annotation changed (untyped -> str | None); parameter 'url' type annotation changed (untyped -> str | None); parameter 'response' type annotation changed (untyped -> BaseHTTPResponse | None); parameter 'error' type annotation changed (untyped -> Exception | None); parameter '_pool' type annotation changed (untyped -> ConnectionPool | None); parameter '_stacktrace' type annotation changed (untyped -> TracebackType | None); return annotation changed (untyped -> Retry) |
| `signature_changed` | `urllib3.util.retry` | `Retry.is_exhausted` | return annotation changed (untyped -> bool) |
| `signature_changed` | `urllib3.util.retry` | `Retry.is_retry` | parameter 'method' type annotation changed (untyped -> str); parameter 'status_code' type annotation changed (untyped -> int); parameter 'has_retry_after' type annotation changed (untyped -> bool); return annotation changed (untyped -> bool) |
| `signature_changed` | `urllib3.util.retry` | `Retry.new` | parameter 'kw' type annotation changed (untyped -> typing.Any); return annotation changed (untyped -> Retry) |
| `signature_changed` | `urllib3.util.retry` | `Retry.parse_retry_after` | parameter 'retry_after' type annotation changed (untyped -> str); return annotation changed (untyped -> float) |
| `signature_changed` | `urllib3.util.retry` | `Retry.sleep_for_retry` | parameter 'response' default removed; parameter 'response' type annotation changed (untyped -> BaseHTTPResponse); return annotation changed (untyped -> bool) |
| `signature_changed` | `urllib3.util.ssl_` | `assert_fingerprint` | parameter 'cert' type annotation changed (untyped -> bytes | None); parameter 'fingerprint' type annotation changed (untyped -> str); return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.util.ssl_` | `create_urllib3_context` | parameter count changed (4 -> 6); return annotation changed (untyped -> ssl.SSLContext) |
| `signature_changed` | `urllib3.util.ssl_` | `is_ipaddress` | parameter 'hostname' type annotation changed (untyped -> str | bytes); return annotation changed (untyped -> bool) |
| `signature_changed` | `urllib3.util.ssl_` | `resolve_cert_reqs` | parameter 'candidate' type annotation changed (untyped -> None | int | str); return annotation changed (untyped -> VerifyMode) |
| `signature_changed` | `urllib3.util.ssl_` | `resolve_ssl_version` | parameter 'candidate' type annotation changed (untyped -> None | int | str); return annotation changed (untyped -> int) |
| `signature_changed` | `urllib3.util.ssl_` | `ssl_wrap_socket` | parameter 'sock' type annotation changed (untyped -> socket.socket); parameter 'keyfile' type annotation changed (untyped -> str | None); parameter 'certfile' type annotation changed (untyped -> str | None); parameter 'cert_reqs' type annotation changed (untyped -> int | None); parameter 'ca_certs' type annotation changed (untyped -> str | None); parameter 'server_hostname' type annotation changed (untyped -> str | None); parameter 'ssl_version' type annotation changed (untyped -> int | None); parameter 'ciphers' type annotation changed (untyped -> str | None); parameter 'ssl_context' type annotation changed (untyped -> ssl.SSLContext | None); parameter 'ca_cert_dir' type annotation changed (untyped -> str | None); parameter 'key_password' type annotation changed (untyped -> str | None); parameter 'ca_cert_data' type annotation changed (untyped -> None | str | bytes); parameter 'tls_in_tls' type annotation changed (untyped -> bool); return annotation changed (untyped -> ssl.SSLSocket | SSLTransportType) |
| `signature_changed` | `urllib3.util.ssl_match_hostname` | `match_hostname` | parameter count changed (2 -> 3); return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.util.ssltransport` | `SSLTransport` | parameter 'socket' type annotation changed (untyped -> socket.socket); parameter 'ssl_context' type annotation changed (untyped -> ssl.SSLContext); parameter 'server_hostname' type annotation changed (untyped -> str | None); parameter 'suppress_ragged_eofs' type annotation changed (untyped -> bool) |
| `signature_changed` | `urllib3.util.ssltransport` | `SSLTransport.cipher` | return annotation changed (untyped -> tuple[str, str, int] | None) |
| `signature_changed` | `urllib3.util.ssltransport` | `SSLTransport.close` | return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.util.ssltransport` | `SSLTransport.compression` | return annotation changed (untyped -> str | None) |
| `signature_changed` | `urllib3.util.ssltransport` | `SSLTransport.fileno` | return annotation changed (untyped -> int) |
| `signature_changed` | `urllib3.util.ssltransport` | `SSLTransport.getpeercert` | parameter 'binary_form' type annotation changed (untyped -> bool); return annotation changed (untyped -> _TYPE_PEER_CERT_RET) |
| `signature_changed` | `urllib3.util.ssltransport` | `SSLTransport.gettimeout` | return annotation changed (untyped -> float | None) |
| `signature_changed` | `urllib3.util.ssltransport` | `SSLTransport.makefile` | parameter 'mode' default removed; parameter 'mode' type annotation changed (untyped -> str); parameter 'buffering' type annotation changed (untyped -> int | None); parameter 'encoding' kind changed (POSITIONAL_OR_KEYWORD -> KEYWORD_ONLY); parameter 'encoding' type annotation changed (untyped -> str | None); parameter 'errors' kind changed (POSITIONAL_OR_KEYWORD -> KEYWORD_ONLY); parameter 'errors' type annotation changed (untyped -> str | None); parameter 'newline' kind changed (POSITIONAL_OR_KEYWORD -> KEYWORD_ONLY); parameter 'newline' type annotation changed (untyped -> str | None); return annotation changed (untyped -> typing.BinaryIO | typing.TextIO | socket.SocketIO) |
| `signature_changed` | `urllib3.util.ssltransport` | `SSLTransport.read` | parameter 'len' type annotation changed (untyped -> int); parameter 'buffer' type annotation changed (untyped -> typing.Any | None); return annotation changed (untyped -> int | bytes) |
| `signature_changed` | `urllib3.util.ssltransport` | `SSLTransport.recv` | parameter 'len' renamed to 'buflen'; parameter 'len' type annotation changed (untyped -> int); parameter 'flags' type annotation changed (untyped -> int); return annotation changed (untyped -> int | bytes) |
| `signature_changed` | `urllib3.util.ssltransport` | `SSLTransport.recv_into` | parameter 'buffer' type annotation changed (untyped -> _WriteBuffer); parameter 'nbytes' type annotation changed (untyped -> int | None); parameter 'flags' type annotation changed (untyped -> int); return annotation changed (untyped -> None | int | bytes) |
| `signature_changed` | `urllib3.util.ssltransport` | `SSLTransport.selected_alpn_protocol` | return annotation changed (untyped -> str | None) |
| `signature_changed` | `urllib3.util.ssltransport` | `SSLTransport.selected_npn_protocol` | return annotation changed (untyped -> str | None) |
| `signature_changed` | `urllib3.util.ssltransport` | `SSLTransport.send` | parameter 'data' type annotation changed (untyped -> bytes); parameter 'flags' type annotation changed (untyped -> int); return annotation changed (untyped -> int) |
| `signature_changed` | `urllib3.util.ssltransport` | `SSLTransport.sendall` | parameter 'data' type annotation changed (untyped -> bytes); parameter 'flags' type annotation changed (untyped -> int); return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.util.ssltransport` | `SSLTransport.settimeout` | parameter 'value' type annotation changed (untyped -> float | None); return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.util.ssltransport` | `SSLTransport.shared_ciphers` | return annotation changed (untyped -> list[tuple[str, str, int]] | None) |
| `signature_changed` | `urllib3.util.ssltransport` | `SSLTransport.unwrap` | return annotation changed (untyped -> None) |
| `signature_changed` | `urllib3.util.ssltransport` | `SSLTransport.version` | return annotation changed (untyped -> str | None) |
| `signature_changed` | `urllib3.util.timeout` | `Timeout` | parameter 'total' type annotation changed (untyped -> _TYPE_TIMEOUT); parameter 'connect' default value changed (<object object at 0xADDR> -> <_TYPE_DEFAULT.token: -1>); parameter 'connect' type annotation changed (untyped -> _TYPE_TIMEOUT); parameter 'read' default value changed (<object object at 0xADDR> -> <_TYPE_DEFAULT.token: -1>); parameter 'read' type annotation changed (untyped -> _TYPE_TIMEOUT) |
| `signature_changed` | `urllib3.util.timeout` | `Timeout.clone` | return annotation changed (untyped -> Timeout) |
| `signature_changed` | `urllib3.util.timeout` | `Timeout.from_float` | parameter 'timeout' type annotation changed (untyped -> _TYPE_TIMEOUT); return annotation changed (untyped -> Timeout) |
| `signature_changed` | `urllib3.util.timeout` | `Timeout.get_connect_duration` | return annotation changed (untyped -> float) |
| `signature_changed` | `urllib3.util.timeout` | `Timeout.resolve_default_timeout` | parameter 'timeout' type annotation changed (untyped -> _TYPE_TIMEOUT); return annotation changed (untyped -> float | None) |
| `signature_changed` | `urllib3.util.timeout` | `Timeout.start_connect` | return annotation changed (untyped -> float) |
| `signature_changed` | `urllib3.util.url` | `Url` | parameter 'scheme' type annotation changed (untyped -> str | None); parameter 'auth' type annotation changed (untyped -> str | None); parameter 'host' type annotation changed (untyped -> str | None); parameter 'port' type annotation changed (untyped -> int | None); parameter 'path' type annotation changed (untyped -> str | None); parameter 'query' type annotation changed (untyped -> str | None); parameter 'fragment' type annotation changed (untyped -> str | None) |
| `signature_changed` | `urllib3.util.url` | `normalize_host` | parameter 'host' type annotation changed (untyped -> str | None); parameter 'scheme' type annotation changed (untyped -> str | None); return annotation changed (untyped -> str | None) |
| `signature_changed` | `urllib3.util.url` | `parse_url` | parameter 'url' type annotation changed (untyped -> str); return annotation changed (untyped -> Url) |
| `signature_changed` | `urllib3.util.wait` | `poll_wait_for_socket` | parameter 'sock' type annotation changed (untyped -> socket.socket); parameter 'read' type annotation changed (untyped -> bool); parameter 'write' type annotation changed (untyped -> bool); parameter 'timeout' type annotation changed (untyped -> float | None); return annotation changed (untyped -> bool) |
| `signature_changed` | `urllib3.util.wait` | `select_wait_for_socket` | parameter 'sock' type annotation changed (untyped -> socket.socket); parameter 'read' type annotation changed (untyped -> bool); parameter 'write' type annotation changed (untyped -> bool); parameter 'timeout' type annotation changed (untyped -> float | None); return annotation changed (untyped -> bool) |
| `signature_changed` | `urllib3.util.wait` | `wait_for_read` | parameter 'sock' type annotation changed (untyped -> socket.socket); parameter 'timeout' type annotation changed (untyped -> float | None); return annotation changed (untyped -> bool) |
| `signature_changed` | `urllib3.util.wait` | `wait_for_socket` | parameter count changed (2 -> 4); return annotation changed (untyped -> bool) |
| `signature_changed` | `urllib3.util.wait` | `wait_for_write` | parameter 'sock' type annotation changed (untyped -> socket.socket); parameter 'timeout' type annotation changed (untyped -> float | None); return annotation changed (untyped -> bool) |
| `removed` | `urllib3.connection` | `HTTPHeaderDict.from_httplib` | Removed public classmethod 'urllib3.connection.HTTPHeaderDict.from_httplib' |
| `removed` | `urllib3.filepost` | `iter_fields` | Removed public function 'urllib3.filepost.iter_fields' |
| `removed` | `urllib3.packages.backports.makefile` | `backport_makefile` | Removed public function 'urllib3.packages.backports.makefile.backport_makefile' |
| `removed` | `urllib3.packages.backports.weakref_finalize` | `weakref_finalize` | Removed public class 'urllib3.packages.backports.weakref_finalize.weakref_finalize' |
| `removed` | `urllib3.packages.backports.weakref_finalize` | `weakref_finalize.detach` | Removed public method 'urllib3.packages.backports.weakref_finalize.weakref_finalize.detach' |
| `removed` | `urllib3.packages.backports.weakref_finalize` | `weakref_finalize.peek` | Removed public method 'urllib3.packages.backports.weakref_finalize.weakref_finalize.peek' |
| `removed` | `urllib3.packages.six` | `Module_six_moves_urllib` | Removed public class 'urllib3.packages.six.Module_six_moves_urllib' |
| `removed` | `urllib3.packages.six` | `Module_six_moves_urllib_error` | Removed public class 'urllib3.packages.six.Module_six_moves_urllib_error' |
| `removed` | `urllib3.packages.six` | `Module_six_moves_urllib_parse` | Removed public class 'urllib3.packages.six.Module_six_moves_urllib_parse' |
| `removed` | `urllib3.packages.six` | `Module_six_moves_urllib_request` | Removed public class 'urllib3.packages.six.Module_six_moves_urllib_request' |
| `removed` | `urllib3.packages.six` | `Module_six_moves_urllib_response` | Removed public class 'urllib3.packages.six.Module_six_moves_urllib_response' |
| `removed` | `urllib3.packages.six` | `Module_six_moves_urllib_robotparser` | Removed public class 'urllib3.packages.six.Module_six_moves_urllib_robotparser' |
| `removed` | `urllib3.packages.six` | `MovedAttribute` | Removed public class 'urllib3.packages.six.MovedAttribute' |
| `removed` | `urllib3.packages.six` | `MovedModule` | Removed public class 'urllib3.packages.six.MovedModule' |
| `removed` | `urllib3.packages.six` | `add_metaclass` | Removed public function 'urllib3.packages.six.add_metaclass' |
| `removed` | `urllib3.packages.six` | `add_move` | Removed public function 'urllib3.packages.six.add_move' |
| `removed` | `urllib3.packages.six` | `assertCountEqual` | Removed public function 'urllib3.packages.six.assertCountEqual' |
| `removed` | `urllib3.packages.six` | `assertNotRegex` | Removed public function 'urllib3.packages.six.assertNotRegex' |
| `removed` | `urllib3.packages.six` | `assertRaisesRegex` | Removed public function 'urllib3.packages.six.assertRaisesRegex' |
| `removed` | `urllib3.packages.six` | `assertRegex` | Removed public function 'urllib3.packages.six.assertRegex' |
| `removed` | `urllib3.packages.six` | `b` | Removed public function 'urllib3.packages.six.b' |
| `removed` | `urllib3.packages.six` | `create_unbound_method` | Removed public function 'urllib3.packages.six.create_unbound_method' |
| `removed` | `urllib3.packages.six` | `ensure_binary` | Removed public function 'urllib3.packages.six.ensure_binary' |
| `removed` | `urllib3.packages.six` | `ensure_str` | Removed public function 'urllib3.packages.six.ensure_str' |
| `removed` | `urllib3.packages.six` | `ensure_text` | Removed public function 'urllib3.packages.six.ensure_text' |
| `removed` | `urllib3.packages.six` | `get_unbound_function` | Removed public function 'urllib3.packages.six.get_unbound_function' |
| `removed` | `urllib3.packages.six` | `iteritems` | Removed public function 'urllib3.packages.six.iteritems' |
| `removed` | `urllib3.packages.six` | `iterkeys` | Removed public function 'urllib3.packages.six.iterkeys' |
| `removed` | `urllib3.packages.six` | `iterlists` | Removed public function 'urllib3.packages.six.iterlists' |
| `removed` | `urllib3.packages.six` | `itervalues` | Removed public function 'urllib3.packages.six.itervalues' |
| `removed` | `urllib3.packages.six` | `python_2_unicode_compatible` | Removed public function 'urllib3.packages.six.python_2_unicode_compatible' |
| `removed` | `urllib3.packages.six` | `raise_from` | Removed public function 'urllib3.packages.six.raise_from' |
| `removed` | `urllib3.packages.six` | `remove_move` | Removed public function 'urllib3.packages.six.remove_move' |
| `removed` | `urllib3.packages.six` | `reraise` | Removed public function 'urllib3.packages.six.reraise' |
| `removed` | `urllib3.packages.six` | `u` | Removed public function 'urllib3.packages.six.u' |
| `removed` | `urllib3.packages.six` | `with_metaclass` | Removed public function 'urllib3.packages.six.with_metaclass' |
| `removed` | `urllib3.poolmanager` | `ProxyConfig` | Removed public class 'urllib3.poolmanager.ProxyConfig' |
| `removed` | `urllib3.request` | `RequestMethods` | Removed public class 'urllib3.request.RequestMethods' |
| `removed` | `urllib3.request` | `RequestMethods.request` | Removed public method 'urllib3.request.RequestMethods.request' |
| `removed` | `urllib3.request` | `RequestMethods.request_encode_body` | Removed public method 'urllib3.request.RequestMethods.request_encode_body' |
| `removed` | `urllib3.request` | `RequestMethods.request_encode_url` | Removed public method 'urllib3.request.RequestMethods.request_encode_url' |
| `removed` | `urllib3.request` | `RequestMethods.urlopen` | Removed public method 'urllib3.request.RequestMethods.urlopen' |
| `removed` | `urllib3.request` | `RequestModule` | Removed public class 'urllib3.request.RequestModule' |
| `removed` | `urllib3.response` | `HTTPResponse.from_httplib` | Removed public classmethod 'urllib3.response.HTTPResponse.from_httplib' |
| `removed` | `urllib3.util.proxy` | `create_proxy_ssl_context` | Removed public function 'urllib3.util.proxy.create_proxy_ssl_context' |
| `removed` | `urllib3.util.queue` | `LifoQueue` | Removed public class 'urllib3.util.queue.LifoQueue' |
| `removed` | `urllib3.util.queue` | `LifoQueue.empty` | Removed public method 'urllib3.util.queue.LifoQueue.empty' |
| `removed` | `urllib3.util.queue` | `LifoQueue.full` | Removed public method 'urllib3.util.queue.LifoQueue.full' |
| `removed` | `urllib3.util.queue` | `LifoQueue.get` | Removed public method 'urllib3.util.queue.LifoQueue.get' |
| `removed` | `urllib3.util.queue` | `LifoQueue.get_nowait` | Removed public method 'urllib3.util.queue.LifoQueue.get_nowait' |
| `removed` | `urllib3.util.queue` | `LifoQueue.join` | Removed public method 'urllib3.util.queue.LifoQueue.join' |
| `removed` | `urllib3.util.queue` | `LifoQueue.put` | Removed public method 'urllib3.util.queue.LifoQueue.put' |
| `removed` | `urllib3.util.queue` | `LifoQueue.put_nowait` | Removed public method 'urllib3.util.queue.LifoQueue.put_nowait' |
| `removed` | `urllib3.util.queue` | `LifoQueue.qsize` | Removed public method 'urllib3.util.queue.LifoQueue.qsize' |
| `removed` | `urllib3.util.queue` | `LifoQueue.task_done` | Removed public method 'urllib3.util.queue.LifoQueue.task_done' |
| `removed` | `urllib3.util.url` | `get_host` | Removed public function 'urllib3.util.url.get_host' |
| `removed` | `urllib3.util.url` | `split_first` | Removed public function 'urllib3.util.url.split_first' |
| `removed` | `urllib3.util.wait` | `null_wait_for_socket` | Removed public function 'urllib3.util.wait.null_wait_for_socket' |
| `added` | `urllib3` | `request` | Added public function 'urllib3.request' |
| `added` | `urllib3.connection` | `ProxyConfig` | Added public class 'urllib3.connection.ProxyConfig' |
| `added` | `urllib3.connectionpool` | `RequestMethods` | Added public class 'urllib3.connectionpool.RequestMethods' |
| `added` | `urllib3.connectionpool` | `RequestMethods.request` | Added public method 'urllib3.connectionpool.RequestMethods.request' |
| `added` | `urllib3.connectionpool` | `RequestMethods.request_encode_body` | Added public method 'urllib3.connectionpool.RequestMethods.request_encode_body' |
| `added` | `urllib3.connectionpool` | `RequestMethods.request_encode_url` | Added public method 'urllib3.connectionpool.RequestMethods.request_encode_url' |
| `added` | `urllib3.connectionpool` | `RequestMethods.urlopen` | Added public method 'urllib3.connectionpool.RequestMethods.urlopen' |
| `added` | `urllib3.fields` | `format_multipart_header_param` | Added public function 'urllib3.fields.format_multipart_header_param' |
| `added` | `urllib3.response` | `BaseHTTPResponse` | Added public class 'urllib3.response.BaseHTTPResponse' |
| `added` | `urllib3.response` | `BaseHTTPResponse.close` | Added public method 'urllib3.response.BaseHTTPResponse.close' |
| `added` | `urllib3.response` | `BaseHTTPResponse.drain_conn` | Added public method 'urllib3.response.BaseHTTPResponse.drain_conn' |
| `added` | `urllib3.response` | `BaseHTTPResponse.get_redirect_location` | Added public method 'urllib3.response.BaseHTTPResponse.get_redirect_location' |
| `added` | `urllib3.response` | `BaseHTTPResponse.getheader` | Added public method 'urllib3.response.BaseHTTPResponse.getheader' |
| `added` | `urllib3.response` | `BaseHTTPResponse.getheaders` | Added public method 'urllib3.response.BaseHTTPResponse.getheaders' |
| `added` | `urllib3.response` | `BaseHTTPResponse.geturl` | Added public method 'urllib3.response.BaseHTTPResponse.geturl' |
| `added` | `urllib3.response` | `BaseHTTPResponse.info` | Added public method 'urllib3.response.BaseHTTPResponse.info' |
| `added` | `urllib3.response` | `BaseHTTPResponse.json` | Added public method 'urllib3.response.BaseHTTPResponse.json' |
| `added` | `urllib3.response` | `BaseHTTPResponse.read` | Added public method 'urllib3.response.BaseHTTPResponse.read' |
| `added` | `urllib3.response` | `BaseHTTPResponse.read_chunked` | Added public method 'urllib3.response.BaseHTTPResponse.read_chunked' |
| `added` | `urllib3.response` | `BaseHTTPResponse.readinto` | Added public method 'urllib3.response.BaseHTTPResponse.readinto' |
| `added` | `urllib3.response` | `BaseHTTPResponse.release_conn` | Added public method 'urllib3.response.BaseHTTPResponse.release_conn' |
| `added` | `urllib3.response` | `BaseHTTPResponse.stream` | Added public method 'urllib3.response.BaseHTTPResponse.stream' |
| `added` | `urllib3.response` | `BytesQueueBuffer` | Added public class 'urllib3.response.BytesQueueBuffer' |
| `added` | `urllib3.response` | `BytesQueueBuffer.get` | Added public method 'urllib3.response.BytesQueueBuffer.get' |
| `added` | `urllib3.response` | `BytesQueueBuffer.put` | Added public method 'urllib3.response.BytesQueueBuffer.put' |
| `added` | `urllib3.response` | `ContentDecoder` | Added public class 'urllib3.response.ContentDecoder' |
| `added` | `urllib3.response` | `ContentDecoder.decompress` | Added public method 'urllib3.response.ContentDecoder.decompress' |
| `added` | `urllib3.response` | `ContentDecoder.flush` | Added public method 'urllib3.response.ContentDecoder.flush' |
| `added` | `urllib3.response` | `DeflateDecoder.flush` | Added public method 'urllib3.response.DeflateDecoder.flush' |
| `added` | `urllib3.response` | `GzipDecoder.flush` | Added public method 'urllib3.response.GzipDecoder.flush' |
| `added` | `urllib3.response` | `HTTPResponse.json` | Added public method 'urllib3.response.HTTPResponse.json' |
| `added` | `urllib3.util.request` | `ChunksAndContentLength` | Added public class 'urllib3.util.request.ChunksAndContentLength' |
| `added` | `urllib3.util.request` | `body_to_chunks` | Added public function 'urllib3.util.request.body_to_chunks' |
| `added` | `urllib3.util.util` | `reraise` | Added public function 'urllib3.util.util.reraise' |
| `added` | `urllib3.util.util` | `to_bytes` | Added public function 'urllib3.util.util.to_bytes' |
| `added` | `urllib3.util.util` | `to_str` | Added public function 'urllib3.util.util.to_str' |

## 3. Discovered Behavioral Drifts (35)

### 3.1 `urllib3.connection.HTTPHeaderDict(headers = None, **kwargs) -> HTTPHeaderDict`
- **Drift Category:** `exception_type_drift` (`fail_to_pass`)
- **Summary:** v1 raised TypeError ('float' object is not iterable), but v2 returned HTTPHeaderDict({}) (urllib3._collections.HTTPHeaderDict)
- **Input Strategy:** `edge_sweep_positional`
- **Original Fuzzed Call:** `HTTPHeaderDict(float('nan'))`
- **Shrunk Minimal Call (1 shrink steps):** `HTTPHeaderDict(0.0)`
- **Baseline (`1.26.18`):** `RAISE TypeError: 'float' object is not iterable`
- **Target (`2.0.7`):** `RETURN HTTPHeaderDict({}) (type: urllib3._collections.HTTPHeaderDict)`

### 3.2 `urllib3.connection.HTTPHeaderDict.<stateful_chain>[stateful chain: add, clear, copy, discard]`
- **Drift Category:** `input_mutation_drift` (`in_place_mutation`)
- **Summary:** Stateful instance mutation drift: attribute '__iter_items__' changed ([{'__t__': 'bytes', 'v': ''}] -> [{'__t__': 'str', 'v': ''}])
- **Input Strategy:** `stateful_call_chain`
- **Original Fuzzed Call:** `obj = HTTPHeaderDict(); obj.add(b'a', ' '); obj.add('a', 'a')`
- **Shrunk Minimal Call (3 shrink steps):** `obj = HTTPHeaderDict(); obj.add(b'', '')`
- **Baseline (`1.26.18`):** `RETURN [None] (type: builtins.list)`
- **Target (`2.0.7`):** `RETURN [None] (type: builtins.list)`
- **Post-Call Mutation Detected:** `args_mutated=(False vs False), instance_mutated=(True vs True)`

### 3.3 `urllib3.connection.HTTPHeaderDict.extend(*args, **kwargs)`
- **Drift Category:** `exception_type_drift` (`fail_to_pass`)
- **Summary:** v1 raised TypeError ('int' object is not iterable), but v2 returned None (builtins.NoneType)
- **Input Strategy:** `varargs_probe`
- **Original Fuzzed Call:** `HTTPHeaderDict.extend(1)`
- **Shrunk Minimal Call (1 shrink steps):** `HTTPHeaderDict.extend(0)`
- **Baseline (`1.26.18`):** `RAISE TypeError: 'int' object is not iterable`
- **Target (`2.0.7`):** `RETURN None (type: builtins.NoneType)`

### 3.4 `urllib3.connection.HTTPHeaderDict.setdefault(key, default = None)`
- **Drift Category:** `input_mutation_drift` (`in_place_mutation`)
- **Summary:** Stateful instance mutation drift: object repr changed ('<repr_error:TypeError>' -> "HTTPHeaderDict({'': ''})")
- **Input Strategy:** `baseline_required`
- **Original Fuzzed Call:** `HTTPHeaderDict.setdefault('')`
- **Shrunk Minimal Call (0 shrink steps):** `HTTPHeaderDict.setdefault('')`
- **Baseline (`1.26.18`):** `RETURN None (type: builtins.NoneType)`
- **Target (`2.0.7`):** `RETURN '' (type: builtins.str)`
- **Post-Call Mutation Detected:** `args_mutated=(False vs False), instance_mutated=(True vs True)`

### 3.5 `urllib3.connectionpool.ConnectionPool(host, port = None) -> ConnectionPool`
- **Drift Category:** `exception_type_drift` (`pass_to_fail`)
- **Summary:** v1 returned <urllib3.connectionpool.ConnectionPool object at 0xADDR> (urllib3.connectionpool.ConnectionPool), but v2 raised TypeError: cannot use a string pattern on a bytes-like object
- **Input Strategy:** `edge_sweep_required`
- **Original Fuzzed Call:** `ConnectionPool(b'a')`
- **Shrunk Minimal Call (0 shrink steps):** `ConnectionPool(b'a')`
- **Baseline (`1.26.18`):** `RETURN <urllib3.connectionpool.ConnectionPool object at 0xADDR> (type: urllib3.connectionpool.ConnectionPool)`
- **Target (`2.0.7`):** `RAISE TypeError: cannot use a string pattern on a bytes-like object`

### 3.6 `urllib3.connectionpool.connection_from_url(url, **kw)`
- **Drift Category:** `return_value_drift` (`value_or_type_mismatch`)
- **Summary:** Return object state drift on <urllib3.connectionpool.HTTPConnectionPool object at 0xADDR> (urllib3.connectionpool.HTTPConnectionPool): attribute 'pool.queue' changed ('deque([None])' -> list([{'__t__': 'none'}])); removed public attribute 'strict'
- **Input Strategy:** `baseline_required`
- **Original Fuzzed Call:** `connection_from_url('https://example.com/path?a=1&b=2#sec')`
- **Shrunk Minimal Call (5 shrink steps):** `connection_from_url('h')`
- **Baseline (`1.26.18`):** `RETURN <urllib3.connectionpool.HTTPConnectionPool object at 0xADDR> (type: urllib3.connectionpool.HTTPConnectionPool)`
- **Target (`2.0.7`):** `RETURN <urllib3.connectionpool.HTTPConnectionPool object at 0xADDR> (type: urllib3.connectionpool.HTTPConnectionPool)`

### 3.7 `urllib3.connectionpool.connection_from_url(url, **kw)`
- **Drift Category:** `return_value_drift` (`value_or_type_mismatch`)
- **Summary:** Return object state drift on <urllib3.connectionpool.HTTPConnectionPool object at 0xADDR> (urllib3.connectionpool.HTTPConnectionPool): attribute 'pool.queue' changed ('deque([None])' -> list([{'__t__': 'none'}])); removed public attribute 'strict'
- **Input Strategy:** `edge_sweep_required`
- **Original Fuzzed Call:** `connection_from_url('http://example.com:8080/test')`
- **Shrunk Minimal Call (4 shrink steps):** `connection_from_url('e')`
- **Baseline (`1.26.18`):** `RETURN <urllib3.connectionpool.HTTPConnectionPool object at 0xADDR> (type: urllib3.connectionpool.HTTPConnectionPool)`
- **Target (`2.0.7`):** `RETURN <urllib3.connectionpool.HTTPConnectionPool object at 0xADDR> (type: urllib3.connectionpool.HTTPConnectionPool)`

### 3.8 `urllib3.fields.RequestField(name, data, filename = None, headers = None, header_formatter = <function format_header_param_html5 at 0xADDR>) -> RequestField`
- **Drift Category:** `return_value_drift` (`value_or_type_mismatch`)
- **Summary:** Return object state drift on <urllib3.fields.RequestField object at 0xADDR> (urllib3.fields.RequestField): removed public attribute 'header_formatter'
- **Input Strategy:** `edge_sweep_positional`
- **Original Fuzzed Call:** `RequestField("The 'header_formatter' parameter is deprecated and will be removed in urllib3 v2.1.0.", {}, None, None, None)`
- **Shrunk Minimal Call (1 shrink steps):** `RequestField('', {}, None, None, None)`
- **Baseline (`1.26.18`):** `RETURN <urllib3.fields.RequestField object at 0xADDR> (type: urllib3.fields.RequestField)`
- **Target (`2.0.7`):** `RETURN <urllib3.fields.RequestField object at 0xADDR> (type: urllib3.fields.RequestField)`

### 3.9 `urllib3.fields.RequestField.<stateful_chain>[stateful chain: make_multipart, render_headers]`
- **Drift Category:** `exception_type_drift` (`exception_class_changed`)
- **Summary:** Exception type changed from TypeError ('expected string or bytes-like object, got 'int'') in v1 to AttributeError (''int' object has no attribute 'translate'') in v2
- **Input Strategy:** `stateful_call_chain`
- **Original Fuzzed Call:** `obj = RequestField(3, {}); obj.make_multipart(); obj.make_multipart()`
- **Shrunk Minimal Call (1 shrink steps):** `obj = RequestField(3, {}); obj.make_multipart()`
- **Baseline (`1.26.18`):** `RAISE TypeError: expected string or bytes-like object, got 'int'`
- **Target (`2.0.7`):** `RAISE AttributeError: 'int' object has no attribute 'translate'`

### 3.10 `urllib3.fields.RequestField.from_tuples(fieldname, value, header_formatter = <function format_header_param_html5 at 0xADDR>)`
- **Drift Category:** `exception_type_drift` (`exception_class_changed`)
- **Summary:** Exception type changed from TypeError ('expected string or bytes-like object, got 'int'') in v1 to AttributeError (''int' object has no attribute 'translate'') in v2
- **Input Strategy:** `baseline_required`
- **Original Fuzzed Call:** `RequestField.from_tuples(3, 3)`
- **Shrunk Minimal Call (2 shrink steps):** `RequestField.from_tuples(0, 0)`
- **Baseline (`1.26.18`):** `RAISE TypeError: expected string or bytes-like object, got 'int'`
- **Target (`2.0.7`):** `RAISE AttributeError: 'int' object has no attribute 'translate'`

### 3.11 `urllib3.fields.RequestField.from_tuples(fieldname, value, header_formatter = <function format_header_param_html5 at 0xADDR>)`
- **Drift Category:** `return_value_drift` (`value_or_type_mismatch`)
- **Summary:** Return object state drift on <urllib3.fields.RequestField object at 0xADDR> (urllib3.fields.RequestField): attribute 'headers' changed ([[{'__t__': 'str', 'v': 'Content-Disposition'}, {'__t__': 'str', 'v': 'form-data; name="%09"'}], [{'__t__': 'str', 'v': 'Content-Type'}, {'__t__': 'none'}], [{'__t__': 'str', 'v': 'Content-Location'}, {'__t__': 'none'}]] -> [[{'__t__': 'str', 'v': 'Content-Disposition'}, {'__t__': 'str', 'v': 'form-data; name="\t"'}], [{'__t__': 'str', 'v': 'Content-Type'}, {'__t__': 'none'}], [{'__t__': 'str', 'v': 'Content-Location'}, {'__t__': 'none'}]])
- **Input Strategy:** `edge_sweep_required`
- **Original Fuzzed Call:** `RequestField.from_tuples('\t\r\n', 3)`
- **Shrunk Minimal Call (2 shrink steps):** `RequestField.from_tuples('\t', 0)`
- **Baseline (`1.26.18`):** `RETURN <urllib3.fields.RequestField object at 0xADDR> (type: urllib3.fields.RequestField)`
- **Target (`2.0.7`):** `RETURN <urllib3.fields.RequestField object at 0xADDR> (type: urllib3.fields.RequestField)`

### 3.12 `urllib3.fields.RequestField.make_multipart(content_disposition = None, content_type = None, content_location = None)`
- **Drift Category:** `exception_type_drift` (`pass_to_fail`)
- **Summary:** v1 returned None (builtins.NoneType), but v2 raised TypeError: can only concatenate list (not "str") to list
- **Input Strategy:** `edge_sweep_positional`
- **Original Fuzzed Call:** `RequestField('Content-Disposition', {}).make_multipart([1, 2])`
- **Shrunk Minimal Call (2 shrink steps):** `RequestField('Content-Disposition', {}).make_multipart([0])`
- **Baseline (`1.26.18`):** `RETURN None (type: builtins.NoneType)`
- **Target (`2.0.7`):** `RAISE TypeError: can only concatenate list (not "str") to list`
- **Post-Call Mutation Detected:** `args_mutated=(True vs False), instance_mutated=(True vs False)`

### 3.13 `urllib3.fields.format_header_param(name, value)`
- **Drift Category:** `exception_type_drift` (`exception_class_changed`)
- **Summary:** Exception type changed from TypeError ('expected string or bytes-like object, got 'int'') in v1 to AttributeError (''int' object has no attribute 'translate'') in v2
- **Input Strategy:** `baseline_required`
- **Original Fuzzed Call:** `format_header_param(2, 2)`
- **Shrunk Minimal Call (2 shrink steps):** `format_header_param(0, 0)`
- **Baseline (`1.26.18`):** `RAISE TypeError: expected string or bytes-like object, got 'int'`
- **Target (`2.0.7`):** `RAISE AttributeError: 'int' object has no attribute 'translate'`

### 3.14 `urllib3.fields.format_header_param(name, value)`
- **Drift Category:** `return_value_drift` (`value_or_type_mismatch`)
- **Summary:** Return value drift: v1 returned '0="%09"' (builtins.str) != v2 returned '0="\t"' (builtins.str)
- **Input Strategy:** `edge_sweep_required`
- **Original Fuzzed Call:** `format_header_param(2, '\t\r\n')`
- **Shrunk Minimal Call (2 shrink steps):** `format_header_param(0, '\t')`
- **Baseline (`1.26.18`):** `RETURN '0="%09"' (type: builtins.str)`
- **Target (`2.0.7`):** `RETURN '0="\t"' (type: builtins.str)`

### 3.15 `urllib3.fields.format_header_param_html5(name, value)`
- **Drift Category:** `exception_type_drift` (`exception_class_changed`)
- **Summary:** Exception type changed from TypeError ('expected string or bytes-like object, got 'int'') in v1 to AttributeError (''int' object has no attribute 'translate'') in v2
- **Input Strategy:** `edge_sweep_required`
- **Original Fuzzed Call:** `format_header_param_html5('utf-8', 2)`
- **Shrunk Minimal Call (2 shrink steps):** `format_header_param_html5('', 0)`
- **Baseline (`1.26.18`):** `RAISE TypeError: expected string or bytes-like object, got 'int'`
- **Target (`2.0.7`):** `RAISE AttributeError: 'int' object has no attribute 'translate'`

### 3.16 `urllib3.fields.format_header_param_html5(name, value)`
- **Drift Category:** `return_value_drift` (`value_or_type_mismatch`)
- **Summary:** Return value drift: v1 returned '="%09"' (builtins.str) != v2 returned '="\t"' (builtins.str)
- **Input Strategy:** `edge_sweep_required`
- **Original Fuzzed Call:** `format_header_param_html5('utf-8', '\t\r\n')`
- **Shrunk Minimal Call (2 shrink steps):** `format_header_param_html5('', '\t')`
- **Baseline (`1.26.18`):** `RETURN '="%09"' (type: builtins.str)`
- **Target (`2.0.7`):** `RETURN '="\t"' (type: builtins.str)`

### 3.17 `urllib3.poolmanager.PoolManager.<stateful_chain>[stateful chain: clear, connection_from_context, connection_from_host, connection_from_pool_key]`
- **Drift Category:** `return_value_drift` (`value_or_type_mismatch`)
- **Summary:** Return object state drift on [<urllib3.connectionpool.HTTPConnectionPool object at 0xADDR>] (builtins.list): attribute '[0].conn_kw' changed ([] -> [[{'__t__': 'str', 'v': 'blocksize'}, {'__t__': 'int', 'v': 16384}]]); attribute '[0].pool.queue' changed ('deque([None])' -> list([{'__t__': 'none'}])); removed public attribute '[0].strict'
- **Input Strategy:** `stateful_call_chain`
- **Original Fuzzed Call:** `obj = PoolManager(); obj.clear(); obj.connection_from_host('a')`
- **Shrunk Minimal Call (1 shrink steps):** `obj = PoolManager(); obj.connection_from_host('a')`
- **Baseline (`1.26.18`):** `RETURN [<urllib3.connectionpool.HTTPConnectionPool object at 0xADDR>] (type: builtins.list)`
- **Target (`2.0.7`):** `RETURN [<urllib3.connectionpool.HTTPConnectionPool object at 0xADDR>] (type: builtins.list)`

### 3.18 `urllib3.poolmanager.PoolManager.connection_from_host(host, port = None, scheme = 'http', pool_kwargs = None)`
- **Drift Category:** `return_value_drift` (`value_or_type_mismatch`)
- **Summary:** Return object state drift on <urllib3.connectionpool.HTTPConnectionPool object at 0xADDR> (urllib3.connectionpool.HTTPConnectionPool): attribute 'conn_kw' changed ([] -> [[{'__t__': 'str', 'v': 'blocksize'}, {'__t__': 'int', 'v': 16384}]]); attribute 'pool.queue' changed ('deque([None])' -> list([{'__t__': 'none'}])); removed public attribute 'strict'
- **Input Strategy:** `baseline_required`
- **Original Fuzzed Call:** `PoolManager.connection_from_host('https://example.com/path?a=1&b=2#sec')`
- **Shrunk Minimal Call (5 shrink steps):** `PoolManager.connection_from_host('h')`
- **Baseline (`1.26.18`):** `RETURN <urllib3.connectionpool.HTTPConnectionPool object at 0xADDR> (type: urllib3.connectionpool.HTTPConnectionPool)`
- **Target (`2.0.7`):** `RETURN <urllib3.connectionpool.HTTPConnectionPool object at 0xADDR> (type: urllib3.connectionpool.HTTPConnectionPool)`

### 3.19 `urllib3.poolmanager.PoolManager.connection_from_url(url, pool_kwargs = None)`
- **Drift Category:** `return_value_drift` (`value_or_type_mismatch`)
- **Summary:** Return object state drift on <urllib3.connectionpool.HTTPConnectionPool object at 0xADDR> (urllib3.connectionpool.HTTPConnectionPool): attribute 'conn_kw' changed ([] -> [[{'__t__': 'str', 'v': 'blocksize'}, {'__t__': 'int', 'v': 16384}]]); attribute 'pool.queue' changed ('deque([None])' -> list([{'__t__': 'none'}])); removed public attribute 'strict'
- **Input Strategy:** `baseline_required`
- **Original Fuzzed Call:** `PoolManager.connection_from_url('https://example.com/path?a=1&b=2#sec')`
- **Shrunk Minimal Call (5 shrink steps):** `PoolManager.connection_from_url('h')`
- **Baseline (`1.26.18`):** `RETURN <urllib3.connectionpool.HTTPConnectionPool object at 0xADDR> (type: urllib3.connectionpool.HTTPConnectionPool)`
- **Target (`2.0.7`):** `RETURN <urllib3.connectionpool.HTTPConnectionPool object at 0xADDR> (type: urllib3.connectionpool.HTTPConnectionPool)`

### 3.20 `urllib3.poolmanager.PoolManager.connection_from_url(url, pool_kwargs = None)`
- **Drift Category:** `return_value_drift` (`value_or_type_mismatch`)
- **Summary:** Return object state drift on <urllib3.connectionpool.HTTPConnectionPool object at 0xADDR> (urllib3.connectionpool.HTTPConnectionPool): attribute 'conn_kw' changed ([] -> [[{'__t__': 'str', 'v': 'blocksize'}, {'__t__': 'int', 'v': 16384}]]); attribute 'pool.queue' changed ('deque([None])' -> list([{'__t__': 'none'}])); removed public attribute 'strict'
- **Input Strategy:** `edge_sweep_required`
- **Original Fuzzed Call:** `PoolManager.connection_from_url('http://example.com:8080/test')`
- **Shrunk Minimal Call (4 shrink steps):** `PoolManager.connection_from_url('e')`
- **Baseline (`1.26.18`):** `RETURN <urllib3.connectionpool.HTTPConnectionPool object at 0xADDR> (type: urllib3.connectionpool.HTTPConnectionPool)`
- **Target (`2.0.7`):** `RETURN <urllib3.connectionpool.HTTPConnectionPool object at 0xADDR> (type: urllib3.connectionpool.HTTPConnectionPool)`

### 3.21 `urllib3.poolmanager.ProxyManager.connection_from_host(host, port = None, scheme = 'http', pool_kwargs = None)`
- **Drift Category:** `return_value_drift` (`value_or_type_mismatch`)
- **Summary:** Return object state drift on <urllib3.connectionpool.HTTPSConnectionPool object at 0xADDR> (urllib3.connectionpool.HTTPSConnectionPool): attribute 'conn_kw' changed ([[{'__t__': 'str', 'v': 'socket_options'}, {'__t__': 'list', 'v': []}], [{'__t__': 'str', 'v': 'proxy'}, {'__t__': 'object', 'cls': 'urllib3.util.url.Url', 'str': 'https://example.com:443/path?a=1&b=2#sec', 'repr': "Url(scheme='https', auth=None, host='example.com', port=443, path='/path', query='a=1&b=2', fragment='sec')", 'state': {'scheme': {'__t__': 'str', 'v': 'https'}, 'auth': {'__t__': 'none'}, 'host': {'__t__': 'str', 'v': 'example.com'}, 'port': {'__t__': 'int', 'v': 443}, 'path': {'__t__': 'str', 'v': '/path'}, 'query': {'__t__': 'str', 'v': 'a=1&b=2'}, 'fragment': {'__t__': 'str', 'v': 'sec'}}}], [{'__t__': 'str', 'v': 'proxy_config'}, {'__t__': 'object', 'cls': 'urllib3.poolmanager.ProxyConfig', 'str': 'ProxyConfig(ssl_context=None, use_forwarding_for_https=False)', 'repr': 'ProxyConfig(ssl_context=None, use_forwarding_for_https=False)', 'state': {'ssl_context': {'__t__': 'none'}, 'use_forwarding_for_https': {'__t__': 'bool', 'v': False}}}]] -> [[{'__t__': 'str', 'v': 'blocksize'}, {'__t__': 'int', 'v': 16384}], [{'__t__': 'str', 'v': 'socket_options'}, {'__t__': 'list', 'v': []}], [{'__t__': 'str', 'v': 'proxy'}, {'__t__': 'object', 'cls': 'urllib3.util.url.Url', 'str': 'https://example.com:443/path?a=1&b=2#sec', 'repr': "Url(scheme='https', auth=None, host='example.com', port=443, path='/path', query='a=1&b=2', fragment='sec')", 'state': {'scheme': {'__t__': 'str', 'v': 'https'}, 'auth': {'__t__': 'none'}, 'host': {'__t__': 'str', 'v': 'example.com'}, 'port': {'__t__': 'int', 'v': 443}, 'path': {'__t__': 'str', 'v': '/path'}, 'query': {'__t__': 'str', 'v': 'a=1&b=2'}, 'fragment': {'__t__': 'str', 'v': 'sec'}}}], [{'__t__': 'str', 'v': 'proxy_config'}, {'__t__': 'object', 'cls': 'urllib3._base_connection.ProxyConfig', 'str': 'ProxyConfig(ssl_context=None, use_forwarding_for_https=False, assert_hostname=None, assert_fingerprint=None)', 'repr': 'ProxyConfig(ssl_context=None, use_forwarding_for_https=False, assert_hostname=None, assert_fingerprint=None)', 'state': {'ssl_context': {'__t__': 'none'}, 'use_forwarding_for_https': {'__t__': 'bool', 'v': False}, 'assert_hostname': {'__t__': 'none'}, 'assert_fingerprint': {'__t__': 'none'}}}]]); attribute 'pool.queue' changed ('deque([None])' -> list([{'__t__': 'none'}])); proxy_config repr changed ('ProxyConfig(ssl_context=None, use_forwarding_for_https=False)' -> 'ProxyConfig(ssl_context=None, use_forwarding_for_https=False, assert_hostname=None, assert_fingerprint=None)'); removed public attribute 'strict'
- **Input Strategy:** `baseline_required`
- **Original Fuzzed Call:** `ProxyManager('https://example.com/path?a=1&b=2#sec').connection_from_host('https://example.com/path?a=1&b=2#sec')`
- **Shrunk Minimal Call (1 shrink steps):** `ProxyManager('https://example.com/path?a=1&b=2#sec').connection_from_host('')`
- **Baseline (`1.26.18`):** `RETURN <urllib3.connectionpool.HTTPSConnectionPool object at 0xADDR> (type: urllib3.connectionpool.HTTPSConnectionPool)`
- **Target (`2.0.7`):** `RETURN <urllib3.connectionpool.HTTPSConnectionPool object at 0xADDR> (type: urllib3.connectionpool.HTTPSConnectionPool)`

### 3.22 `urllib3.poolmanager.ProxyManager.connection_from_host(host, port = None, scheme = 'http', pool_kwargs = None)`
- **Drift Category:** `return_value_drift` (`value_or_type_mismatch`)
- **Summary:** Return object state drift on <urllib3.connectionpool.HTTPConnectionPool object at 0xADDR> (urllib3.connectionpool.HTTPConnectionPool): attribute 'conn_kw' changed ([[{'__t__': 'str', 'v': 'socket_options'}, {'__t__': 'list', 'v': []}], [{'__t__': 'str', 'v': 'proxy'}, {'__t__': 'object', 'cls': 'urllib3.util.url.Url', 'str': 'http://example.com:8080/test', 'repr': "Url(scheme='http', auth=None, host='example.com', port=8080, path='/test', query=None, fragment=None)", 'state': {'scheme': {'__t__': 'str', 'v': 'http'}, 'auth': {'__t__': 'none'}, 'host': {'__t__': 'str', 'v': 'example.com'}, 'port': {'__t__': 'int', 'v': 8080}, 'path': {'__t__': 'str', 'v': '/test'}, 'query': {'__t__': 'none'}, 'fragment': {'__t__': 'none'}}}], [{'__t__': 'str', 'v': 'proxy_config'}, {'__t__': 'object', 'cls': 'urllib3.poolmanager.ProxyConfig', 'str': 'ProxyConfig(ssl_context=None, use_forwarding_for_https=False)', 'repr': 'ProxyConfig(ssl_context=None, use_forwarding_for_https=False)', 'state': {'ssl_context': {'__t__': 'none'}, 'use_forwarding_for_https': {'__t__': 'bool', 'v': False}}}]] -> [[{'__t__': 'str', 'v': 'blocksize'}, {'__t__': 'int', 'v': 16384}], [{'__t__': 'str', 'v': 'socket_options'}, {'__t__': 'list', 'v': []}], [{'__t__': 'str', 'v': 'proxy'}, {'__t__': 'object', 'cls': 'urllib3.util.url.Url', 'str': 'http://example.com:8080/test', 'repr': "Url(scheme='http', auth=None, host='example.com', port=8080, path='/test', query=None, fragment=None)", 'state': {'scheme': {'__t__': 'str', 'v': 'http'}, 'auth': {'__t__': 'none'}, 'host': {'__t__': 'str', 'v': 'example.com'}, 'port': {'__t__': 'int', 'v': 8080}, 'path': {'__t__': 'str', 'v': '/test'}, 'query': {'__t__': 'none'}, 'fragment': {'__t__': 'none'}}}], [{'__t__': 'str', 'v': 'proxy_config'}, {'__t__': 'object', 'cls': 'urllib3._base_connection.ProxyConfig', 'str': 'ProxyConfig(ssl_context=None, use_forwarding_for_https=False, assert_hostname=None, assert_fingerprint=None)', 'repr': 'ProxyConfig(ssl_context=None, use_forwarding_for_https=False, assert_hostname=None, assert_fingerprint=None)', 'state': {'ssl_context': {'__t__': 'none'}, 'use_forwarding_for_https': {'__t__': 'bool', 'v': False}, 'assert_hostname': {'__t__': 'none'}, 'assert_fingerprint': {'__t__': 'none'}}}]]); attribute 'pool.queue' changed ('deque([None])' -> list([{'__t__': 'none'}])); proxy_config repr changed ('ProxyConfig(ssl_context=None, use_forwarding_for_https=False)' -> 'ProxyConfig(ssl_context=None, use_forwarding_for_https=False, assert_hostname=None, assert_fingerprint=None)'); removed public attribute 'strict'
- **Input Strategy:** `baseline_required`
- **Original Fuzzed Call:** `ProxyManager('http://example.com:8080/test').connection_from_host('https://example.com/path?a=1&b=2#sec')`
- **Shrunk Minimal Call (1 shrink steps):** `ProxyManager('http://example.com:8080/test').connection_from_host('')`
- **Baseline (`1.26.18`):** `RETURN <urllib3.connectionpool.HTTPConnectionPool object at 0xADDR> (type: urllib3.connectionpool.HTTPConnectionPool)`
- **Target (`2.0.7`):** `RETURN <urllib3.connectionpool.HTTPConnectionPool object at 0xADDR> (type: urllib3.connectionpool.HTTPConnectionPool)`

### 3.23 `urllib3.poolmanager.ProxyManager.connection_from_url(url, pool_kwargs = None)`
- **Drift Category:** `return_value_drift` (`value_or_type_mismatch`)
- **Summary:** Return object state drift on <urllib3.connectionpool.HTTPSConnectionPool object at 0xADDR> (urllib3.connectionpool.HTTPSConnectionPool): attribute 'conn_kw' changed ([[{'__t__': 'str', 'v': 'socket_options'}, {'__t__': 'list', 'v': []}], [{'__t__': 'str', 'v': 'proxy'}, {'__t__': 'object', 'cls': 'urllib3.util.url.Url', 'str': 'https://example.com:443/path?a=1&b=2#sec', 'repr': "Url(scheme='https', auth=None, host='example.com', port=443, path='/path', query='a=1&b=2', fragment='sec')", 'state': {'scheme': {'__t__': 'str', 'v': 'https'}, 'auth': {'__t__': 'none'}, 'host': {'__t__': 'str', 'v': 'example.com'}, 'port': {'__t__': 'int', 'v': 443}, 'path': {'__t__': 'str', 'v': '/path'}, 'query': {'__t__': 'str', 'v': 'a=1&b=2'}, 'fragment': {'__t__': 'str', 'v': 'sec'}}}], [{'__t__': 'str', 'v': 'proxy_config'}, {'__t__': 'object', 'cls': 'urllib3.poolmanager.ProxyConfig', 'str': 'ProxyConfig(ssl_context=None, use_forwarding_for_https=False)', 'repr': 'ProxyConfig(ssl_context=None, use_forwarding_for_https=False)', 'state': {'ssl_context': {'__t__': 'none'}, 'use_forwarding_for_https': {'__t__': 'bool', 'v': False}}}]] -> [[{'__t__': 'str', 'v': 'blocksize'}, {'__t__': 'int', 'v': 16384}], [{'__t__': 'str', 'v': 'socket_options'}, {'__t__': 'list', 'v': []}], [{'__t__': 'str', 'v': 'proxy'}, {'__t__': 'object', 'cls': 'urllib3.util.url.Url', 'str': 'https://example.com:443/path?a=1&b=2#sec', 'repr': "Url(scheme='https', auth=None, host='example.com', port=443, path='/path', query='a=1&b=2', fragment='sec')", 'state': {'scheme': {'__t__': 'str', 'v': 'https'}, 'auth': {'__t__': 'none'}, 'host': {'__t__': 'str', 'v': 'example.com'}, 'port': {'__t__': 'int', 'v': 443}, 'path': {'__t__': 'str', 'v': '/path'}, 'query': {'__t__': 'str', 'v': 'a=1&b=2'}, 'fragment': {'__t__': 'str', 'v': 'sec'}}}], [{'__t__': 'str', 'v': 'proxy_config'}, {'__t__': 'object', 'cls': 'urllib3._base_connection.ProxyConfig', 'str': 'ProxyConfig(ssl_context=None, use_forwarding_for_https=False, assert_hostname=None, assert_fingerprint=None)', 'repr': 'ProxyConfig(ssl_context=None, use_forwarding_for_https=False, assert_hostname=None, assert_fingerprint=None)', 'state': {'ssl_context': {'__t__': 'none'}, 'use_forwarding_for_https': {'__t__': 'bool', 'v': False}, 'assert_hostname': {'__t__': 'none'}, 'assert_fingerprint': {'__t__': 'none'}}}]]); attribute 'pool.queue' changed ('deque([None])' -> list([{'__t__': 'none'}])); proxy_config repr changed ('ProxyConfig(ssl_context=None, use_forwarding_for_https=False)' -> 'ProxyConfig(ssl_context=None, use_forwarding_for_https=False, assert_hostname=None, assert_fingerprint=None)'); removed public attribute 'strict'
- **Input Strategy:** `baseline_required`
- **Original Fuzzed Call:** `ProxyManager('https://example.com/path?a=1&b=2#sec').connection_from_url('https://example.com/path?a=1&b=2#sec')`
- **Shrunk Minimal Call (1 shrink steps):** `ProxyManager('https://example.com/path?a=1&b=2#sec').connection_from_url('')`
- **Baseline (`1.26.18`):** `RETURN <urllib3.connectionpool.HTTPSConnectionPool object at 0xADDR> (type: urllib3.connectionpool.HTTPSConnectionPool)`
- **Target (`2.0.7`):** `RETURN <urllib3.connectionpool.HTTPSConnectionPool object at 0xADDR> (type: urllib3.connectionpool.HTTPSConnectionPool)`

### 3.24 `urllib3.poolmanager.ProxyManager.connection_from_url(url, pool_kwargs = None)`
- **Drift Category:** `return_value_drift` (`value_or_type_mismatch`)
- **Summary:** Return object state drift on <urllib3.connectionpool.HTTPConnectionPool object at 0xADDR> (urllib3.connectionpool.HTTPConnectionPool): attribute 'conn_kw' changed ([[{'__t__': 'str', 'v': 'socket_options'}, {'__t__': 'list', 'v': []}], [{'__t__': 'str', 'v': 'proxy'}, {'__t__': 'object', 'cls': 'urllib3.util.url.Url', 'str': 'http://example.com:8080/test', 'repr': "Url(scheme='http', auth=None, host='example.com', port=8080, path='/test', query=None, fragment=None)", 'state': {'scheme': {'__t__': 'str', 'v': 'http'}, 'auth': {'__t__': 'none'}, 'host': {'__t__': 'str', 'v': 'example.com'}, 'port': {'__t__': 'int', 'v': 8080}, 'path': {'__t__': 'str', 'v': '/test'}, 'query': {'__t__': 'none'}, 'fragment': {'__t__': 'none'}}}], [{'__t__': 'str', 'v': 'proxy_config'}, {'__t__': 'object', 'cls': 'urllib3.poolmanager.ProxyConfig', 'str': 'ProxyConfig(ssl_context=None, use_forwarding_for_https=False)', 'repr': 'ProxyConfig(ssl_context=None, use_forwarding_for_https=False)', 'state': {'ssl_context': {'__t__': 'none'}, 'use_forwarding_for_https': {'__t__': 'bool', 'v': False}}}]] -> [[{'__t__': 'str', 'v': 'blocksize'}, {'__t__': 'int', 'v': 16384}], [{'__t__': 'str', 'v': 'socket_options'}, {'__t__': 'list', 'v': []}], [{'__t__': 'str', 'v': 'proxy'}, {'__t__': 'object', 'cls': 'urllib3.util.url.Url', 'str': 'http://example.com:8080/test', 'repr': "Url(scheme='http', auth=None, host='example.com', port=8080, path='/test', query=None, fragment=None)", 'state': {'scheme': {'__t__': 'str', 'v': 'http'}, 'auth': {'__t__': 'none'}, 'host': {'__t__': 'str', 'v': 'example.com'}, 'port': {'__t__': 'int', 'v': 8080}, 'path': {'__t__': 'str', 'v': '/test'}, 'query': {'__t__': 'none'}, 'fragment': {'__t__': 'none'}}}], [{'__t__': 'str', 'v': 'proxy_config'}, {'__t__': 'object', 'cls': 'urllib3._base_connection.ProxyConfig', 'str': 'ProxyConfig(ssl_context=None, use_forwarding_for_https=False, assert_hostname=None, assert_fingerprint=None)', 'repr': 'ProxyConfig(ssl_context=None, use_forwarding_for_https=False, assert_hostname=None, assert_fingerprint=None)', 'state': {'ssl_context': {'__t__': 'none'}, 'use_forwarding_for_https': {'__t__': 'bool', 'v': False}, 'assert_hostname': {'__t__': 'none'}, 'assert_fingerprint': {'__t__': 'none'}}}]]); attribute 'pool.queue' changed ('deque([None])' -> list([{'__t__': 'none'}])); proxy_config repr changed ('ProxyConfig(ssl_context=None, use_forwarding_for_https=False)' -> 'ProxyConfig(ssl_context=None, use_forwarding_for_https=False, assert_hostname=None, assert_fingerprint=None)'); removed public attribute 'strict'
- **Input Strategy:** `edge_sweep_required`
- **Original Fuzzed Call:** `ProxyManager('http://example.com:8080/test').connection_from_url('http://example.com:8080/test')`
- **Shrunk Minimal Call (1 shrink steps):** `ProxyManager('http://example.com:8080/test').connection_from_url('')`
- **Baseline (`1.26.18`):** `RETURN <urllib3.connectionpool.HTTPConnectionPool object at 0xADDR> (type: urllib3.connectionpool.HTTPConnectionPool)`
- **Target (`2.0.7`):** `RETURN <urllib3.connectionpool.HTTPConnectionPool object at 0xADDR> (type: urllib3.connectionpool.HTTPConnectionPool)`

### 3.25 `urllib3.poolmanager.proxy_from_url(url, **kw)`
- **Drift Category:** `return_value_drift` (`value_or_type_mismatch`)
- **Summary:** Return object state drift on <urllib3.poolmanager.ProxyManager object at 0xADDR> (urllib3.poolmanager.ProxyManager): attribute 'connection_pool_kw' changed ([[{'__t__': 'str', 'v': '_proxy'}, {'__t__': 'object', 'cls': 'urllib3.util.url.Url', 'str': 'https://:443', 'repr': "Url(scheme='https', auth=None, host=None, port=443, path=None, query=None, fragment=None)", 'state': {'scheme': {'__t__': 'str', 'v': 'https'}, 'auth': {'__t__': 'none'}, 'host': {'__t__': 'none'}, 'port': {'__t__': 'int', 'v': 443}, 'path': {'__t__': 'none'}, 'query': {'__t__': 'none'}, 'fragment': {'__t__': 'none'}}}], [{'__t__': 'str', 'v': '_proxy_headers'}, {'__t__': 'dict', 'v': []}], [{'__t__': 'str', 'v': '_proxy_config'}, {'__t__': 'object', 'cls': 'urllib3.poolmanager.ProxyConfig', 'str': 'ProxyConfig(ssl_context=None, use_forwarding_for_https=False)', 'repr': 'ProxyConfig(ssl_context=None, use_forwarding_for_https=False)', 'state': {'ssl_context': {'__t__': 'none'}, 'use_forwarding_for_https': {'__t__': 'bool', 'v': False}}}]] -> [[{'__t__': 'str', 'v': '_proxy'}, {'__t__': 'object', 'cls': 'urllib3.util.url.Url', 'str': 'https://:443', 'repr': "Url(scheme='https', auth=None, host=None, port=443, path=None, query=None, fragment=None)", 'state': {'scheme': {'__t__': 'str', 'v': 'https'}, 'auth': {'__t__': 'none'}, 'host': {'__t__': 'none'}, 'port': {'__t__': 'int', 'v': 443}, 'path': {'__t__': 'none'}, 'query': {'__t__': 'none'}, 'fragment': {'__t__': 'none'}}}], [{'__t__': 'str', 'v': '_proxy_headers'}, {'__t__': 'dict', 'v': []}], [{'__t__': 'str', 'v': '_proxy_config'}, {'__t__': 'object', 'cls': 'urllib3._base_connection.ProxyConfig', 'str': 'ProxyConfig(ssl_context=None, use_forwarding_for_https=False, assert_hostname=None, assert_fingerprint=None)', 'repr': 'ProxyConfig(ssl_context=None, use_forwarding_for_https=False, assert_hostname=None, assert_fingerprint=None)', 'state': {'ssl_context': {'__t__': 'none'}, 'use_forwarding_for_https': {'__t__': 'bool', 'v': False}, 'assert_hostname': {'__t__': 'none'}, 'assert_fingerprint': {'__t__': 'none'}}}]]); proxy_config repr changed ('ProxyConfig(ssl_context=None, use_forwarding_for_https=False)' -> 'ProxyConfig(ssl_context=None, use_forwarding_for_https=False, assert_hostname=None, assert_fingerprint=None)')
- **Input Strategy:** `baseline_required`
- **Original Fuzzed Call:** `proxy_from_url('https://example.com/path?a=1&b=2#sec')`
- **Shrunk Minimal Call (5 shrink steps):** `proxy_from_url('https:')`
- **Baseline (`1.26.18`):** `RETURN <urllib3.poolmanager.ProxyManager object at 0xADDR> (type: urllib3.poolmanager.ProxyManager)`
- **Target (`2.0.7`):** `RETURN <urllib3.poolmanager.ProxyManager object at 0xADDR> (type: urllib3.poolmanager.ProxyManager)`

### 3.26 `urllib3.response.HTTPResponse.read(amt = None, decode_content = None, cache_content = False)`
- **Drift Category:** `exception_type_drift` (`pass_to_fail`)
- **Summary:** v1 returned None (builtins.NoneType), but v2 raised TypeError: '>=' not supported between instances of 'int' and 'str'
- **Input Strategy:** `edge_sweep_positional`
- **Original Fuzzed Call:** `HTTPResponse.read('')`
- **Shrunk Minimal Call (0 shrink steps):** `HTTPResponse.read('')`
- **Baseline (`1.26.18`):** `RETURN None (type: builtins.NoneType)`
- **Target (`2.0.7`):** `RAISE TypeError: '>=' not supported between instances of 'int' and 'str'`

### 3.27 `urllib3.response.HTTPResponse.read(amt = None, decode_content = None, cache_content = False)`
- **Drift Category:** `return_value_drift` (`value_or_type_mismatch`)
- **Summary:** Return value drift: v1 returned None (builtins.NoneType) != v2 returned b'' (builtins.bytes)
- **Input Strategy:** `edge_sweep_positional`
- **Original Fuzzed Call:** `HTTPResponse.read(0)`
- **Shrunk Minimal Call (0 shrink steps):** `HTTPResponse.read(0)`
- **Baseline (`1.26.18`):** `RETURN None (type: builtins.NoneType)`
- **Target (`2.0.7`):** `RETURN b'' (type: builtins.bytes)`

### 3.28 `urllib3.response.HTTPResponse.read(amt = None, decode_content = None, cache_content = False)`
- **Drift Category:** `exception_type_drift` (`pass_to_fail`)
- **Summary:** v1 returned None (builtins.NoneType), but v2 raised RuntimeError: buffer is empty
- **Input Strategy:** `edge_sweep_positional`
- **Original Fuzzed Call:** `HTTPResponse.read(-1)`
- **Shrunk Minimal Call (0 shrink steps):** `HTTPResponse.read(-1)`
- **Baseline (`1.26.18`):** `RETURN None (type: builtins.NoneType)`
- **Target (`2.0.7`):** `RAISE RuntimeError: buffer is empty`

### 3.29 `urllib3.response.HTTPResponse.readinto(b)`
- **Drift Category:** `exception_type_drift` (`fail_to_pass`)
- **Summary:** v1 raised TypeError (object of type 'NoneType' has no len()), but v2 returned 0 (builtins.int)
- **Input Strategy:** `baseline_required`
- **Original Fuzzed Call:** `HTTPResponse.readinto('')`
- **Shrunk Minimal Call (0 shrink steps):** `HTTPResponse.readinto('')`
- **Baseline (`1.26.18`):** `RAISE TypeError: object of type 'NoneType' has no len()`
- **Target (`2.0.7`):** `RETURN 0 (type: builtins.int)`

### 3.30 `urllib3.util.connection.is_connection_dropped(conn)`
- **Drift Category:** `exception_type_drift` (`pass_to_fail`)
- **Summary:** v1 returned False (builtins.bool), but v2 raised AttributeError: 'str' object has no attribute 'is_connected'
- **Input Strategy:** `baseline_required`
- **Original Fuzzed Call:** `is_connection_dropped('')`
- **Shrunk Minimal Call (0 shrink steps):** `is_connection_dropped('')`
- **Baseline (`1.26.18`):** `RETURN False (type: builtins.bool)`
- **Target (`2.0.7`):** `RAISE AttributeError: 'str' object has no attribute 'is_connected'`

### 3.31 `urllib3.util.retry.Retry.sleep_for_retry(response = None)`
- **Drift Category:** `exception_type_drift` (`exception_class_changed`)
- **Summary:** Exception type changed from AttributeError (''NoneType' object has no attribute 'headers'') in v1 to TypeError ('Retry.sleep_for_retry() missing 1 required positional argument: 'response'') in v2
- **Input Strategy:** `defaults_only`
- **Original Fuzzed Call:** `Retry.sleep_for_retry()`
- **Shrunk Minimal Call (0 shrink steps):** `Retry.sleep_for_retry()`
- **Baseline (`1.26.18`):** `RAISE AttributeError: 'NoneType' object has no attribute 'headers'`
- **Target (`2.0.7`):** `RAISE TypeError: Retry.sleep_for_retry() missing 1 required positional argument: 'response'`

### 3.32 `urllib3.util.ssl_.create_urllib3_context(ssl_version = None, cert_reqs = None, options = None, ciphers = None)`
- **Drift Category:** `return_value_drift` (`value_or_type_mismatch`)
- **Summary:** Return object state drift on <ssl.SSLContext object at 0xADDR> (ssl.SSLContext): attribute 'hostname_checks_common_name' changed (True -> False)
- **Input Strategy:** `defaults_only`
- **Original Fuzzed Call:** `create_urllib3_context()`
- **Shrunk Minimal Call (0 shrink steps):** `create_urllib3_context()`
- **Baseline (`1.26.18`):** `RETURN <ssl.SSLContext object at 0xADDR> (type: ssl.SSLContext)`
- **Target (`2.0.7`):** `RETURN <ssl.SSLContext object at 0xADDR> (type: ssl.SSLContext)`

### 3.33 `urllib3.util.ssl_.create_urllib3_context(ssl_version = None, cert_reqs = None, options = None, ciphers = None)`
- **Drift Category:** `exception_type_drift` (`fail_to_pass`)
- **Summary:** v1 raised TypeError ('str' object cannot be interpreted as an integer), but v2 returned <ssl.SSLContext object at 0xADDR> (ssl.SSLContext)
- **Input Strategy:** `edge_sweep_positional`
- **Original Fuzzed Call:** `create_urllib3_context('1.0.0')`
- **Shrunk Minimal Call (2 shrink steps):** `create_urllib3_context('1')`
- **Baseline (`1.26.18`):** `RAISE TypeError: 'str' object cannot be interpreted as an integer`
- **Target (`2.0.7`):** `RETURN <ssl.SSLContext object at 0xADDR> (type: ssl.SSLContext)`

### 3.34 `urllib3.util.ssl_.create_urllib3_context(ssl_version = None, cert_reqs = None, options = None, ciphers = None)`
- **Drift Category:** `exception_type_drift` (`fail_to_pass`)
- **Summary:** v1 raised ValueError (invalid or unsupported protocol version 1), but v2 returned <ssl.SSLContext object at 0xADDR> (ssl.SSLContext)
- **Input Strategy:** `edge_sweep_positional`
- **Original Fuzzed Call:** `create_urllib3_context(-1)`
- **Shrunk Minimal Call (13 shrink steps):** `create_urllib3_context(1)`
- **Baseline (`1.26.18`):** `RAISE ValueError: invalid or unsupported protocol version 1`
- **Target (`2.0.7`):** `RETURN <ssl.SSLContext object at 0xADDR> (type: ssl.SSLContext)`

### 3.35 `urllib3.util.ssl_.ssl_wrap_socket(sock, keyfile = None, certfile = None, cert_reqs = None, ca_certs = None, server_hostname = None, ssl_version = None, ciphers = None, ssl_context = None, ca_cert_dir = None, key_password = None, ca_cert_data = None, tls_in_tls = False)`
- **Drift Category:** `exception_type_drift` (`exception_class_changed`)
- **Summary:** Exception type changed from TypeError (''str' object cannot be interpreted as an integer') in v1 to AttributeError (''str' object has no attribute 'getsockopt'') in v2
- **Input Strategy:** `edge_sweep_positional`
- **Original Fuzzed Call:** `ssl_wrap_socket('', None, None, None, None, None, '1.0.0')`
- **Shrunk Minimal Call (2 shrink steps):** `ssl_wrap_socket('', None, None, None, None, None, '1')`
- **Baseline (`1.26.18`):** `RAISE TypeError: 'str' object cannot be interpreted as an integer`
- **Target (`2.0.7`):** `RAISE AttributeError: 'str' object has no attribute 'getsockopt'`
