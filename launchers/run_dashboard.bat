@echo off
title Task Controller Dashboard
cd /d "%~dp0\.."

echo ======================================================
echo   Task Controller - Web Dashboard Launcher
echo ======================================================
echo Starting local web server...
echo Browser will open automatically at http://127.0.0.1:18500
echo (Press Ctrl+C to stop)
echo.

python core\server.py
pause
