# Run from any directory: powershell -ExecutionPolicy Bypass -File .\start-frontend.ps1
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
Write-Host 'Starting SentinelScan dashboard at http://localhost:5173 (Ctrl+C to stop)' -ForegroundColor Green
py -3 -m http.server 5173 --bind 127.0.0.1 --directory frontend/dist
