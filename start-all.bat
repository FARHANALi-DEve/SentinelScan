@echo off
cd /d "%~dp0"
start "SentinelScan Backend" powershell -NoExit -ExecutionPolicy Bypass -File "%~dp0start-backend.ps1"
start "SentinelScan Dashboard" powershell -NoExit -ExecutionPolicy Bypass -File "%~dp0start-frontend.ps1"
echo Open http://localhost:5173 after the two terminal windows finish starting.
pause
