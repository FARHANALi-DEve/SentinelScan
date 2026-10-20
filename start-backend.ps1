# Run from any directory: powershell -ExecutionPolicy Bypass -File .\start-backend.ps1
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (-not (Test-Path '.venv\Scripts\python.exe')) {
    Write-Host 'Creating Python virtual environment...' -ForegroundColor Cyan
    py -3 -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Python 3 missing. Install Python 3.10+ from python.org.' }
}
$Python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
& $Python -m pip install -r backend\requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
$env:PYTHONPATH = Join-Path $PSScriptRoot 'backend'
Write-Host 'Starting SentinelScan API at http://127.0.0.1:8000 (Ctrl+C to stop)' -ForegroundColor Green
& $Python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
