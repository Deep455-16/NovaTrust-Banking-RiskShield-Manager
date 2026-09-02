@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul 2>nul

set "ROOT=%~dp0"
set "BACKEND_URL=http://127.0.0.1:8000/api/v1/health"
set "FRONTEND_URL=http://127.0.0.1:3000"

echo.
echo =====================================================
echo   RiskShield AI Manager - Launcher
echo =====================================================
echo.

:: ─────────────────────────────────────────────────────
:: Check backend venv
:: ─────────────────────────────────────────────────────
if not exist "%ROOT%backend\.venv\Scripts\python.exe" (
  echo [!] Backend environment not found. Running install.bat first...
  call "%ROOT%install.bat"
  if errorlevel 1 (
    echo [ERROR] Installation failed. Please contact support.
    pause
    exit /b 1
  )
)

:: ─────────────────────────────────────────────────────
:: Check frontend node_modules and next binary
:: ─────────────────────────────────────────────────────
if not exist "%ROOT%frontend\node_modules\.bin\next.cmd" (
  echo [!] Frontend dependencies not found. Running install.bat first...
  call "%ROOT%install.bat"
  if errorlevel 1 (
    echo [ERROR] Installation failed. Please contact support.
    pause
    exit /b 1
  )
)

:: ─────────────────────────────────────────────────────
:: Resolve npm path (works even if not on system PATH)
:: ─────────────────────────────────────────────────────
set "NPM_CMD="
where npm >nul 2>nul && set "NPM_CMD=npm"
if not defined NPM_CMD (
  if exist "%ProgramFiles%\nodejs\npm.cmd" set "NPM_CMD=%ProgramFiles%\nodejs\npm.cmd"
)
if not defined NPM_CMD (
  if exist "%APPDATA%\nvm\nodejs\npm.cmd" set "NPM_CMD=%APPDATA%\nvm\nodejs\npm.cmd"
)
if not defined NPM_CMD (
  echo [ERROR] npm not found. Please run install.bat first.
  pause
  exit /b 1
)

:: ─────────────────────────────────────────────────────
:: Resolve Ollama and start it
:: ─────────────────────────────────────────────────────
set "OLLAMA_EXE="
where ollama >nul 2>nul && set "OLLAMA_EXE=ollama"
if not defined OLLAMA_EXE (
  if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" set "OLLAMA_EXE=%LOCALAPPDATA%\Programs\Ollama\ollama.exe"
)
if defined OLLAMA_EXE (
  echo Starting Ollama AI server in background...
  start /b "" "%OLLAMA_EXE%" serve
  timeout /t 3 /nobreak >nul
)

:: ─────────────────────────────────────────────────────
:: Start Backend
:: ─────────────────────────────────────────────────────
echo [1/2] Starting RiskShield Backend API on port 8000...
start /b cmd /c "cd /d "%ROOT%backend" && call ".venv\Scripts\activate.bat" && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 2>&1"

:: ─────────────────────────────────────────────────────
:: Start Frontend (production build preferred, dev fallback)
:: ─────────────────────────────────────────────────────
echo [2/2] Starting RiskShield Frontend UI on port 3000...
if exist "%ROOT%frontend\.next\standalone\server.js" (
  echo   Using pre-built production build...
  start /b cmd /c "cd /d "%ROOT%frontend" && node .next\standalone\server.js 2>&1"
) else (
  echo   Starting in development mode (next dev)...
  start /b cmd /c "cd /d "%ROOT%frontend" && call "%NPM_CMD%" run dev -- -H 127.0.0.1 -p 3000 2>&1"
)

echo.
echo Waiting for services to start (this may take up to 2 minutes)...

:: Wait for backend
set /a attempts=0
:wait_backend
timeout /t 3 /nobreak >nul
set /a attempts+=1
powershell -NoProfile -Command "try { $r = Invoke-WebRequest -UseBasicParsing '%BACKEND_URL%' -TimeoutSec 2; exit 0 } catch { exit 1 }" >nul 2>nul
if not errorlevel 1 goto backend_ok
if %attempts% lss 40 goto wait_backend
echo [ERROR] Backend did not start in time. Check if port 8000 is in use.
pause
exit /b 1
:backend_ok
echo   Backend is running!

:: Wait for frontend
set /a attempts=0
:wait_frontend
timeout /t 3 /nobreak >nul
set /a attempts+=1
powershell -NoProfile -Command "try { $r = Invoke-WebRequest -UseBasicParsing '%FRONTEND_URL%' -TimeoutSec 2; exit 0 } catch { exit 1 }" >nul 2>nul
if not errorlevel 1 goto frontend_ok
if %attempts% lss 40 goto wait_frontend
echo [ERROR] Frontend did not start in time. Check if port 3000 is in use.
pause
exit /b 1
:frontend_ok
echo   Frontend is running!

echo.
echo Opening RiskShield AI Manager in browser...
start http://127.0.0.1:3000

echo.
echo =====================================================
echo   RiskShield AI Manager is running!
echo   Backend:  http://127.0.0.1:8000
echo   Frontend: http://127.0.0.1:3000
echo   Keep this window open to keep the app running.
echo   Press Ctrl+C to stop all services.
echo =====================================================
echo.

:loop
timeout /t 3600 >nul
goto loop
