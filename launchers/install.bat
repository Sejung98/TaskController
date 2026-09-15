@echo off
title Task Controller - Dependency Installer
cd /d "%~dp0\.."

echo ======================================================
echo   Task Controller - Dependency Installer
echo ======================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to PATH.
    echo Please install Python 3.8 or higher from https://www.python.org/
    echo Remember to check "Add python.exe to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [1/2] Upgrading pip...
python -m pip install --upgrade pip

echo.
echo [2/2] Installing dependencies (pystray, Pillow, psutil)...
python -m pip install -r requirements.txt

echo.
echo ======================================================
echo   [SUCCESS] Dependencies installed!
echo   Launch scripts are located in the launchers\ folder:
echo     - launchers\run_tray.bat       (System tray mode)
echo     - launchers\run_dashboard.bat  (Web dashboard mode)
echo ======================================================
echo.
pause
