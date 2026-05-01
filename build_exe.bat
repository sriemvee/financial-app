@echo off
:: ============================================================
:: build_exe.bat — Build financial_app.exe with PyInstaller
:: Run this script once to produce the distributable .exe
:: ============================================================

setlocal EnableDelayedExpansion

echo ============================================================
echo  Financial App — EXE Builder
echo ============================================================
echo.

:: ── 1. Check Python ─────────────────────────────────────────
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not on PATH.
    echo         Download it from https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python found.

:: ── 2. Install / upgrade PyInstaller ────────────────────────
echo.
echo Installing PyInstaller...
pip install --upgrade pyinstaller
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install PyInstaller.
    pause
    exit /b 1
)
echo [OK] PyInstaller ready.

:: ── 3. Build the executable ─────────────────────────────────
echo.
echo Building financial_app.exe ...
echo.

pyinstaller ^
    --onefile ^
    --console ^
    --name financial_app ^
    --distpath dist ^
    --workpath build ^
    app_launcher.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] PyInstaller build failed. Check the output above.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  Build complete!
echo.
echo  Executable : dist\financial_app.exe
echo.
echo  HOW TO USE:
echo    1. Copy  dist\financial_app.exe  next to your
echo       backend\  and  frontend\  folders.
echo    2. Double-click  financial_app.exe
echo    3. The browser opens automatically at http://localhost:5173
echo    4. Press Ctrl+C in the console window to stop all services.
echo ============================================================
echo.
pause
