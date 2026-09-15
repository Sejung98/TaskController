@echo off
title Stop Task Controller
cd /d "%~dp0\.."

echo ======================================================
echo   Stopping Task Controller Background Processes...
echo ======================================================

python -c "import os, psutil; [p.kill() for p in psutil.process_iter(['pid','cmdline']) if p.info['pid'] != os.getpid() and any(x in ' '.join(p.info['cmdline'] or []) for x in ['TaskController', 'tray.py', 'server.py', 'core\\server.py'])]" 2>nul

echo [OK] Task Controller processes stopped successfully.
ping 127.0.0.1 -n 2 > nul
