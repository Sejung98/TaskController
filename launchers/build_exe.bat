@echo off
title Task Controller - Build Standalone EXE
cd /d "%~dp0\.."

echo ======================================================
echo   Task Controller - Standalone EXE Builder
echo   Compiles standalone .exe (No Python required for end users)
echo ======================================================
echo.

where pyinstaller >nul 2>nul
if %errorlevel% neq 0 (
    echo [INFO] PyInstaller not found. Installing pyinstaller...
    python -m pip install pyinstaller
)

echo.
echo [INFO] Building standalone TaskController.exe...
echo Please wait...
echo.

pyinstaller --noconsole --onefile ^
  --icon="assets\icon.ico" ^
  --name="TaskController" ^
  --add-data "web;web" ^
  --add-data "assets;assets" ^
  --add-data "core;core" ^
  --clean ^
  tray.py

if %errorlevel% equ 0 (
    echo.
    echo ======================================================
    echo   [SUCCESS] Build Completed!
    echo   Standalone executable: dist\TaskController.exe
    echo   You can upload this file to GitHub Releases!
    echo ======================================================
) else (
    echo.
    echo [ERROR] Build failed. Please review the output above.
)

echo.
pause
