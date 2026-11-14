# VerDiff Differential Analysis: `sqlparse` (`0.4.3` -> `0.4.4`)

## 1. Executive Telemetry Summary

| Metric | Value |
| :--- | :--- |
| **Package** | `sqlparse` |
| **Version A (Baseline)** | `0.4.3` |
| **Version B (Target)** | `0.4.4` |
| **Python Runtime** | `3.12.14` |
| **Deterministic Seed** | `42` |
| **Public Callables (`v1` / `v2`)** | `556` / `560` |
| **Unchanged Signatures** | `554` |
| **Static Signature Changes** | `2` |
| **Callables & Chains Fuzzed** | `120` |
| **Synthesized Inputs Executed** | `4262` |
| **Non-Breaking Object Noise Filtered** | `0` |
| **Max Drifts Ceiling (`--max-drifts`)** | `Unlimited (0)` |
| **Silent Behavioral Drifts Found** | **`22`** |
| **Wall-Clock Duration** | `20.94s` |

## 2. Static API Surface Changes (8)

| Change Kind | Module | Symbol (`v1` -> `v2`) | Signature / Details |
| :--- | :--- | :--- | :--- |
| `removed` | `sqlparse.compat` | `unicode_compatible` | Removed public function 'sqlparse.compat.unicode_compatible' |
| `removed` | `sqlparse.keywords` | `is_keyword` | Removed public function 'sqlparse.keywords.is_keyword' |
| `added` | `sqlparse.lexer` | `Lexer.add_keywords` | Added public method 'sqlparse.lexer.Lexer.add_keywords' |
| `added` | `sqlparse.lexer` | `Lexer.clear` | Added public method 'sqlparse.lexer.Lexer.clear' |
| `added` | `sqlparse.lexer` | `Lexer.default_initialization` | Added public method 'sqlparse.lexer.Lexer.default_initialization' |
| `added` | `sqlparse.lexer` | `Lexer.get_default_instance` | Added public classmethod 'sqlparse.lexer.Lexer.get_default_instance' |
| `added` | `sqlparse.lexer` | `Lexer.is_keyword` | Added public method 'sqlparse.lexer.Lexer.is_keyword' |
| `added` | `sqlparse.lexer` | `Lexer.set_SQL_REGEX` | Added public method 'sqlparse.lexer.Lexer.set_SQL_REGEX' |

## 3. Discovered Behavioral Drifts (22)

### 3.1 `sqlparse.lexer.Lexer.get_tokens(text, encoding = None)`
- **Drift Category:** `exception_type_drift` (`pass_to_fail`)
- **Summary:** v1 returned [(Token.Operator.Comparison, '<')] (builtins.list), but v2 raised AttributeError: 'Lexer' object has no attribute '_SQL_REGEX'
- **Input Strategy:** `baseline_required`
- **Original Fuzzed Call:** `Lexer.get_tokens('<p>Hello <b>World</b></p>')`
- **Shrunk Minimal Call (4 shrink steps):** `Lexer.get_tokens('<')`
- **Baseline (`0.4.3`):** `RETURN [(Token.Operator.Comparison, '<')] (type: builtins.list)`
- **Target (`0.4.4`):** `RAISE AttributeError: 'Lexer' object has no attribute '_SQL_REGEX'`

### 3.2 `sqlparse.lexer.tokenize(sql, encoding = None)`
- **Drift Category:** `latency_regression` (`124.0x_latency_shift`)
- **Summary:** Latency shift (124.0x faster in v2 / pathological in v1): v1 median 40.13ms -> v2 median 0.32ms
- **Input Strategy:** `baseline_required`
- **Original Fuzzed Call:** `tokenize("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\")`
- **Shrunk Minimal Call (0 shrink steps):** `tokenize("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\")`
- **Baseline (`0.4.3`):** `RETURN [(Token.Error, "'"), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token (type: builtins.list) [40.13ms median]`
- **Target (`0.4.4`):** `RETURN [(Token.Error, "'"), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token (type: builtins.list) [0.32ms median]`

### 3.3 `sqlparse.lexer.tokenize(sql, encoding = None)`
- **Drift Category:** `latency_regression` (`120.7x_latency_shift`)
- **Summary:** Latency shift (120.7x faster in v2 / pathological in v1): v1 median 40.25ms -> v2 median 0.33ms
- **Input Strategy:** `edge_sweep_positional`
- **Original Fuzzed Call:** `tokenize("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", None)`
- **Shrunk Minimal Call (0 shrink steps):** `tokenize("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", None)`
- **Baseline (`0.4.3`):** `RETURN [(Token.Error, "'"), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token (type: builtins.list) [40.25ms median]`
- **Target (`0.4.4`):** `RETURN [(Token.Error, "'"), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token (type: builtins.list) [0.33ms median]`

### 3.4 `sqlparse.lexer.tokenize(sql, encoding = None)`
- **Drift Category:** `return_value_drift` (`value_or_type_mismatch`)
- **Summary:** Return value drift: v1 returned [(Token.Operator.Comparison, 'IN')] (builtins.list) != v2 returned [(Token.Keyword, 'IN')] (builtins.list)
- **Input Strategy:** `edge_sweep_required`
- **Original Fuzzed Call:** `tokenize('SELECT 1 WHERE a IN (1);')`
- **Shrunk Minimal Call (5 shrink steps):** `tokenize('IN')`
- **Baseline (`0.4.3`):** `RETURN [(Token.Operator.Comparison, 'IN')] (type: builtins.list)`
- **Target (`0.4.4`):** `RETURN [(Token.Keyword, 'IN')] (type: builtins.list)`

### 3.5 `sqlparse.lexer.tokenize(sql, encoding = None)`
- **Drift Category:** `latency_regression` (`123.6x_latency_shift`)
- **Summary:** Latency shift (123.6x faster in v2 / pathological in v1): v1 median 39.82ms -> v2 median 0.32ms
- **Input Strategy:** `edge_sweep_positional`
- **Original Fuzzed Call:** `tokenize("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", ' ')`
- **Shrunk Minimal Call (0 shrink steps):** `tokenize("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", ' ')`
- **Baseline (`0.4.3`):** `RETURN [(Token.Error, "'"), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token (type: builtins.list) [39.82ms median]`
- **Target (`0.4.4`):** `RETURN [(Token.Error, "'"), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token.Error, '\\'), (Token (type: builtins.list) [0.32ms median]`

### 3.6 `sqlparse.engine.filter_stack.FilterStack.<stateful_chain>[stateful chain: enable_grouping, run]`
- **Drift Category:** `return_value_drift` (`value_or_type_mismatch`)
- **Summary:** Return object state drift on [[<Statement 'RE a I...' at 0xADDR>]] (builtins.list): [0][0].tokens[0] ("<Name 'RE' at 0xADDR>" -> "<Name 'RE' at 0xADDR>"); [0][0].tokens[1] ("<Whitespace ' ' at 0xADDR>" -> "<Whitespace ' ' at 0xADDR>"); [0][0].tokens[2] ("<Name 'a' at 0xADDR>" -> "<Name 'a' at 0xADDR>")
- **Input Strategy:** `stateful_call_chain`
- **Original Fuzzed Call:** `obj = FilterStack(); obj.run('a'); obj.run('SELECT 1 WHERE a IN (1);'); obj.run(b'a')`
- **Shrunk Minimal Call (3 shrink steps):** `obj = FilterStack(); obj.run('RE a IN (1);')`
- **Baseline (`0.4.3`):** `RETURN [[<Statement 'RE a I...' at 0xADDR>]] (type: builtins.list)`
- **Target (`0.4.4`):** `RETURN [[<Statement 'RE a I...' at 0xADDR>]] (type: builtins.list)`

### 3.7 `sqlparse.format(sql, encoding = None, **options)`
- **Drift Category:** `latency_regression` (`114.0x_latency_shift`)
- **Summary:** Latency shift (114.0x faster in v2 / pathological in v1): v1 median 41.11ms -> v2 median 0.36ms
- **Input Strategy:** `baseline_required`
- **Original Fuzzed Call:** `format("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\")`
- **Shrunk Minimal Call (0 shrink steps):** `format("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\")`
- **Baseline (`0.4.3`):** `RETURN "'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\" (type: builtins.str) [41.11ms median]`
- **Target (`0.4.4`):** `RETURN "'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\" (type: builtins.str) [0.36ms median]`

### 3.8 `sqlparse.format(sql, encoding = None, **options)`
- **Drift Category:** `latency_regression` (`111.0x_latency_shift`)
- **Summary:** Latency shift (111.0x faster in v2 / pathological in v1): v1 median 40.74ms -> v2 median 0.37ms
- **Input Strategy:** `edge_sweep_positional`
- **Original Fuzzed Call:** `format("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", None)`
- **Shrunk Minimal Call (0 shrink steps):** `format("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", None)`
- **Baseline (`0.4.3`):** `RETURN "'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\" (type: builtins.str) [40.74ms median]`
- **Target (`0.4.4`):** `RETURN "'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\" (type: builtins.str) [0.37ms median]`

### 3.9 `sqlparse.format(sql, encoding = None, **options)`
- **Drift Category:** `latency_regression` (`115.7x_latency_shift`)
- **Summary:** Latency shift (115.7x faster in v2 / pathological in v1): v1 median 41.09ms -> v2 median 0.35ms
- **Input Strategy:** `edge_sweep_positional`
- **Original Fuzzed Call:** `format("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", '')`
- **Shrunk Minimal Call (0 shrink steps):** `format("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", '')`
- **Baseline (`0.4.3`):** `RETURN "'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\" (type: builtins.str) [41.09ms median]`
- **Target (`0.4.4`):** `RETURN "'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\" (type: builtins.str) [0.35ms median]`

### 3.10 `sqlparse.format(sql, encoding = None, **options)`
- **Drift Category:** `latency_regression` (`109.7x_latency_shift`)
- **Summary:** Latency shift (109.7x faster in v2 / pathological in v1): v1 median 40.79ms -> v2 median 0.37ms
- **Input Strategy:** `edge_sweep_positional`
- **Original Fuzzed Call:** `format("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", '_diff')`
- **Shrunk Minimal Call (0 shrink steps):** `format("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", '_diff')`
- **Baseline (`0.4.3`):** `RETURN "'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\" (type: builtins.str) [40.79ms median]`
- **Target (`0.4.4`):** `RETURN "'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\" (type: builtins.str) [0.37ms median]`

### 3.11 `sqlparse.format(sql, encoding = None, **options)`
- **Drift Category:** `latency_regression` (`111.4x_latency_shift`)
- **Summary:** Latency shift (111.4x faster in v2 / pathological in v1): v1 median 41.14ms -> v2 median 0.37ms
- **Input Strategy:** `edge_sweep_positional`
- **Original Fuzzed Call:** `format("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", ' ')`
- **Shrunk Minimal Call (0 shrink steps):** `format("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", ' ')`
- **Baseline (`0.4.3`):** `RETURN "'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\" (type: builtins.str) [41.14ms median]`
- **Target (`0.4.4`):** `RETURN "'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\" (type: builtins.str) [0.37ms median]`

### 3.12 `sqlparse.parse(sql, encoding = None)`
- **Drift Category:** `latency_regression` (`46.0x_latency_shift`)
- **Summary:** Latency shift (46.0x faster in v2 / pathological in v1): v1 median 42.03ms -> v2 median 0.91ms
- **Input Strategy:** `baseline_required`
- **Original Fuzzed Call:** `parse("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\")`
- **Shrunk Minimal Call (0 shrink steps):** `parse("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\")`
- **Baseline (`0.4.3`):** `RETURN (<Statement ''\\\\\...' at 0xADDR>,) (type: builtins.tuple) [42.03ms median]`
- **Target (`0.4.4`):** `RETURN (<Statement ''\\\\\...' at 0xADDR>,) (type: builtins.tuple) [0.91ms median]`

### 3.13 `sqlparse.parse(sql, encoding = None)`
- **Drift Category:** `latency_regression` (`48.4x_latency_shift`)
- **Summary:** Latency shift (48.4x faster in v2 / pathological in v1): v1 median 41.06ms -> v2 median 0.85ms
- **Input Strategy:** `edge_sweep_positional`
- **Original Fuzzed Call:** `parse("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", None)`
- **Shrunk Minimal Call (0 shrink steps):** `parse("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", None)`
- **Baseline (`0.4.3`):** `RETURN (<Statement ''\\\\\...' at 0xADDR>,) (type: builtins.tuple) [41.06ms median]`
- **Target (`0.4.4`):** `RETURN (<Statement ''\\\\\...' at 0xADDR>,) (type: builtins.tuple) [0.85ms median]`

### 3.14 `sqlparse.parse(sql, encoding = None)`
- **Drift Category:** `latency_regression` (`50.4x_latency_shift`)
- **Summary:** Latency shift (50.4x faster in v2 / pathological in v1): v1 median 42.24ms -> v2 median 0.84ms
- **Input Strategy:** `edge_sweep_positional`
- **Original Fuzzed Call:** `parse("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", '')`
- **Shrunk Minimal Call (0 shrink steps):** `parse("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", '')`
- **Baseline (`0.4.3`):** `RETURN (<Statement ''\\\\\...' at 0xADDR>,) (type: builtins.tuple) [42.24ms median]`
- **Target (`0.4.4`):** `RETURN (<Statement ''\\\\\...' at 0xADDR>,) (type: builtins.tuple) [0.84ms median]`

### 3.15 `sqlparse.parse(sql, encoding = None)`
- **Drift Category:** `return_value_drift` (`value_or_type_mismatch`)
- **Summary:** Return object state drift on (<Statement 'IN' at 0xADDR>,) (builtins.tuple): attribute '[0].tokens[0].is_keyword' changed (False -> True); attribute '[0].tokens[0].parent' changed ("<Statement 'IN' at 0xADDR>" -> "<Statement 'IN' at 0xADDR>"); attribute '[0].tokens[0].ttype' changed ('Token.Operator.Comparison' -> 'Token.Keyword')
- **Input Strategy:** `edge_sweep_required`
- **Original Fuzzed Call:** `parse('SELECT 1 WHERE a IN (1);')`
- **Shrunk Minimal Call (5 shrink steps):** `parse('IN')`
- **Baseline (`0.4.3`):** `RETURN (<Statement 'IN' at 0xADDR>,) (type: builtins.tuple)`
- **Target (`0.4.4`):** `RETURN (<Statement 'IN' at 0xADDR>,) (type: builtins.tuple)`

### 3.16 `sqlparse.parse(sql, encoding = None)`
- **Drift Category:** `latency_regression` (`50.2x_latency_shift`)
- **Summary:** Latency shift (50.2x faster in v2 / pathological in v1): v1 median 41.68ms -> v2 median 0.83ms
- **Input Strategy:** `edge_sweep_positional`
- **Original Fuzzed Call:** `parse("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", ' ')`
- **Shrunk Minimal Call (0 shrink steps):** `parse("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", ' ')`
- **Baseline (`0.4.3`):** `RETURN (<Statement ''\\\\\...' at 0xADDR>,) (type: builtins.tuple) [41.68ms median]`
- **Target (`0.4.4`):** `RETURN (<Statement ''\\\\\...' at 0xADDR>,) (type: builtins.tuple) [0.83ms median]`

### 3.17 `sqlparse.parsestream(stream, encoding = None)`
- **Drift Category:** `latency_regression` (`65.2x_latency_shift`)
- **Summary:** Latency shift (65.2x faster in v2 / pathological in v1): v1 median 49.26ms -> v2 median 0.76ms
- **Input Strategy:** `edge_sweep_required`
- **Original Fuzzed Call:** `parsestream("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\")`
- **Shrunk Minimal Call (0 shrink steps):** `parsestream("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\")`
- **Baseline (`0.4.3`):** `RETURN [<Statement ''\\\\\...' at 0xADDR>] (type: builtins.list) [49.26ms median]`
- **Target (`0.4.4`):** `RETURN [<Statement ''\\\\\...' at 0xADDR>] (type: builtins.list) [0.76ms median]`

### 3.18 `sqlparse.split(sql, encoding = None)`
- **Drift Category:** `latency_regression` (`141.6x_latency_shift`)
- **Summary:** Latency shift (141.6x faster in v2 / pathological in v1): v1 median 45.96ms -> v2 median 0.32ms
- **Input Strategy:** `baseline_required`
- **Original Fuzzed Call:** `split("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\")`
- **Shrunk Minimal Call (0 shrink steps):** `split("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\")`
- **Baseline (`0.4.3`):** `RETURN ["'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\"] (type: builtins.list) [45.96ms median]`
- **Target (`0.4.4`):** `RETURN ["'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\"] (type: builtins.list) [0.32ms median]`

### 3.19 `sqlparse.split(sql, encoding = None)`
- **Drift Category:** `latency_regression` (`149.2x_latency_shift`)
- **Summary:** Latency shift (149.2x faster in v2 / pathological in v1): v1 median 48.69ms -> v2 median 0.33ms
- **Input Strategy:** `edge_sweep_positional`
- **Original Fuzzed Call:** `split("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", None)`
- **Shrunk Minimal Call (0 shrink steps):** `split("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", None)`
- **Baseline (`0.4.3`):** `RETURN ["'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\"] (type: builtins.list) [48.69ms median]`
- **Target (`0.4.4`):** `RETURN ["'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\"] (type: builtins.list) [0.33ms median]`

### 3.20 `sqlparse.split(sql, encoding = None)`
- **Drift Category:** `latency_regression` (`150.6x_latency_shift`)
- **Summary:** Latency shift (150.6x faster in v2 / pathological in v1): v1 median 48.86ms -> v2 median 0.32ms
- **Input Strategy:** `edge_sweep_positional`
- **Original Fuzzed Call:** `split("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", '')`
- **Shrunk Minimal Call (0 shrink steps):** `split("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", '')`
- **Baseline (`0.4.3`):** `RETURN ["'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\"] (type: builtins.list) [48.86ms median]`
- **Target (`0.4.4`):** `RETURN ["'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\"] (type: builtins.list) [0.32ms median]`

### 3.21 `sqlparse.split(sql, encoding = None)`
- **Drift Category:** `latency_regression` (`139.0x_latency_shift`)
- **Summary:** Latency shift (139.0x faster in v2 / pathological in v1): v1 median 45.45ms -> v2 median 0.33ms
- **Input Strategy:** `edge_sweep_positional`
- **Original Fuzzed Call:** `split("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", ' ')`
- **Shrunk Minimal Call (0 shrink steps):** `split("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", ' ')`
- **Baseline (`0.4.3`):** `RETURN ["'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\"] (type: builtins.list) [45.45ms median]`
- **Target (`0.4.4`):** `RETURN ["'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\"] (type: builtins.list) [0.33ms median]`

### 3.22 `sqlparse.split(sql, encoding = None)`
- **Drift Category:** `latency_regression` (`154.0x_latency_shift`)
- **Summary:** Latency shift (154.0x faster in v2 / pathological in v1): v1 median 50.45ms -> v2 median 0.33ms
- **Input Strategy:** `edge_sweep_positional`
- **Original Fuzzed Call:** `split("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", '\t\r\n')`
- **Shrunk Minimal Call (0 shrink steps):** `split("'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\", '\t\r\n')`
- **Baseline (`0.4.3`):** `RETURN ["'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\"] (type: builtins.list) [50.45ms median]`
- **Target (`0.4.4`):** `RETURN ["'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\"] (type: builtins.list) [0.33ms median]`
