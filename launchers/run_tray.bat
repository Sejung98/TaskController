@echo off
title Task Controller Tray
cd /d "%~dp0\.."

echo ======================================================
echo   Task Controller - System Tray Launcher
echo ======================================================
echo Starting background system tray process...
start "" pythonw.exe "tray.py"

echo.
echo [OK] Running in background.
echo Look for the controller icon in your Windows notification area (near the clock).
ping 127.0.0.1 -n 3 > nul
