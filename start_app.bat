@echo off
:: ============================================================
:: start_app.bat — Simple batch-file fallback launcher
:: Opens two console windows (backend + frontend) and then
:: launches the browser.  No Python packaging required.
:: ============================================================

setlocal EnableDelayedExpansion

echo ============================================================
echo  Financial App — Quick Start
echo ============================================================
echo.

:: ── Check Python ────────────────────────────────────────────
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not on PATH.
    echo         Download it from https://www.python.org/downloads/
    pause
    exit /b 1
)

:: ── Check Node / npm ────────────────────────────────────────
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js is not installed or not on PATH.
    echo         Download it from https://nodejs.org/
    pause
    exit /b 1
)

where npm >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] npm is not installed or not on PATH.
    pause
    exit /b 1
)

echo [OK] All dependencies found.
echo.

:: ── Start Backend ───────────────────────────────────────────
echo Starting Backend  (http://localhost:8000) ...
start "Financial App — Backend" cmd /k "cd /d "%~dp0backend" && python -m uvicorn main:app --reload --port 8000"

:: ── Wait a moment then start Frontend ───────────────────────
timeout /t 2 /nobreak >nul

echo Starting Frontend (http://localhost:5173) ...
start "Financial App — Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

:: ── Wait for services then open browser ─────────────────────
echo.
echo Waiting for services to start...
timeout /t 6 /nobreak >nul

echo Opening browser...
start "" "http://localhost:5173"

echo.
echo ============================================================
echo  Financial App is running!
echo.
echo  Backend  ^> http://localhost:8000
echo  Frontend ^> http://localhost:5173
echo.
echo  Close the Backend and Frontend console windows to stop.
echo ============================================================
echo.
pause
