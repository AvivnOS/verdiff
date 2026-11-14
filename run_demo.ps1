$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

$env:UV_CACHE_DIR = Join-Path $ProjectRoot ".cache\pkg_cache\uv"
$env:PIP_CACHE_DIR = Join-Path $ProjectRoot ".cache\pkg_cache\pip"
$env:PYTHONUTF8 = "1"

$VenvDir = Join-Path $ProjectRoot ".venv"
$PythonExe = Join-Path $VenvDir "Scripts\python.exe"

if (-not (Test-Path $PythonExe)) {
    Write-Host "[VerDiff] Provisioning primary virtual environment (.venv)..." -ForegroundColor Cyan
    uv venv $VenvDir --python 3.12
    uv pip install --python $PythonExe -e "$ProjectRoot[dev]"
}

$ReportsDir = Join-Path $ProjectRoot "reports"
if (Test-Path $ReportsDir) {
    Get-ChildItem -Path "$ReportsDir\*" -Include "*.py", "*.md", "*.html" | Remove-Item -Force
}

Write-Host "`n=== [1/3] Running VerDiff Core Test Suite ===" -ForegroundColor Cyan
& $PythonExe -m pytest "$ProjectRoot\tests" -v
if ($LASTEXITCODE -ne 0) { throw "Core test suite failed" }

Write-Host "`n=== [2/3] Running Unfiltered Differential Fuzzing on 5 Real PyPI Upgrades (Minor, Patch & Major) ===" -ForegroundColor Cyan

# 1. Minor Upgrade Control (Honest 0 Drifts, 0 False Positives): packaging 23.0 -> 23.1
& $PythonExe -m verdiff.cli packaging 23.0 23.1 --output-dir "$ReportsDir"
if ($LASTEXITCODE -ne 0) { throw "VerDiff run failed for packaging 23.0 -> 23.1" }

# 2. Minor Upgrade (Silent Marker & Requirement Parsing Shifts): packaging 23.1 -> 23.2
& $PythonExe -m verdiff.cli packaging 23.1 23.2 --output-dir "$ReportsDir"
if ($LASTEXITCODE -ne 0) { throw "VerDiff run failed for packaging 23.1 -> 23.2" }

# 3. Patch Upgrade (Latency Shift, Lexer.get_tokens AttributeError & IN Keyword Drift): sqlparse 0.4.3 -> 0.4.4
& $PythonExe -m verdiff.cli sqlparse 0.4.3 0.4.4 --output-dir "$ReportsDir"
if ($LASTEXITCODE -ne 0) { throw "VerDiff run failed for sqlparse 0.4.3 -> 0.4.4" }

# 4. Patch Upgrade (Cookie Header Redirect Stripping & Default Blocksize Shift): urllib3 2.0.2 -> 2.0.7
& $PythonExe -m verdiff.cli urllib3 2.0.2 2.0.7 --output-dir "$ReportsDir"
if ($LASTEXITCODE -ne 0) { throw "VerDiff run failed for urllib3 2.0.2 -> 2.0.7" }

# 5. Major Upgrade (Stateful HTTPHeaderDict Input Mutation, View Objects & Sentinel Filtering): urllib3 1.26.18 -> 2.0.7
& $PythonExe -m verdiff.cli urllib3 1.26.18 2.0.7 --output-dir "$ReportsDir"
if ($LASTEXITCODE -ne 0) { throw "VerDiff run failed for urllib3 1.26.18 -> 2.0.7" }

Write-Host "`n=== [3/3] Executing Auto-Generated Standalone Pytest Reproduction Suites ===" -ForegroundColor Cyan
& $PythonExe -m pytest "$ReportsDir" -v
if ($LASTEXITCODE -ne 0) { throw "Auto-generated standalone reproduction suite failed" }

Write-Host "`n[VerDiff] All 5 unfiltered benchmarks and standalone reproduction suites passed." -ForegroundColor Green
