@echo off
setlocal EnableDelayedExpansion

set "ROOT=%~dp0"
set "BACKEND_URL=http://127.0.0.1:8000/api/v1/health"
set "FRONTEND_URL=http://127.0.0.1:3000"

echo.
echo =====================================================
echo   RiskShield AI Manager - Launcher
echo =====================================================
echo.

:: Kill anything already on port 8000 or 3000
echo Freeing ports 8000 and 3000...
for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":8000 " 2^>nul') do taskkill /PID %%P /F >nul 2>nul
for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":3000 " 2^>nul') do taskkill /PID %%P /F >nul 2>nul
timeout /t 2 /nobreak >nul

:: Check backend venv
if not exist "%ROOT%backend\.venv\Scripts\python.exe" (
  echo [!] Backend not found. Running install.bat...
  call "%ROOT%install.bat"
  if errorlevel 1 ( echo [ERROR] Install failed. & pause & exit /b 1 )
)

:: Check frontend node_modules
if not exist "%ROOT%frontend\node_modules\.bin\next.cmd" (
  echo [!] Frontend not found. Running install.bat...
  call "%ROOT%install.bat"
  if errorlevel 1 ( echo [ERROR] Install failed. & pause & exit /b 1 )
)

:: Resolve npm
set "NPM_CMD=npm"
where npm >nul 2>nul
if errorlevel 1 if exist "%ProgramFiles%\nodejs\npm.cmd" set "NPM_CMD=%ProgramFiles%\nodejs\npm.cmd"

:: Start Ollama only if not already on port 11434
netstat -ano | findstr ":11434 " >nul 2>nul
if errorlevel 1 (
  set "OLLAMA_EXE="
  where ollama >nul 2>nul && set "OLLAMA_EXE=ollama"
  if not defined OLLAMA_EXE if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" set "OLLAMA_EXE=%LOCALAPPDATA%\Programs\Ollama\ollama.exe"
  if defined OLLAMA_EXE (
    echo Starting Ollama AI server...
    start /b "" "%OLLAMA_EXE%" serve
    timeout /t 3 /nobreak >nul
  )
) else (
  echo Ollama already running.
)

:: ── Start Backend in background (output shown in THIS window) ──
echo.
echo [1/2] Starting Backend API on port 8000...
set "BACK_DIR=%ROOT%backend"
set "FRONT_DIR=%ROOT%frontend"

echo @echo off > "%TEMP%\rs_backend.cmd"
echo cd /d "%BACK_DIR%" >> "%TEMP%\rs_backend.cmd"
echo call ".venv\Scripts\activate.bat" >> "%TEMP%\rs_backend.cmd"
echo python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 >> "%TEMP%\rs_backend.cmd"

echo @echo off > "%TEMP%\rs_frontend.cmd"
echo cd /d "%FRONT_DIR%" >> "%TEMP%\rs_frontend.cmd"
echo "%NPM_CMD%" run dev -- -H 127.0.0.1 -p 3000 >> "%TEMP%\rs_frontend.cmd"

:: Run both in background within this same window
start /b cmd /c "%TEMP%\rs_backend.cmd"

:: ── Wait for backend ──
echo Waiting for Backend to start...
set /a attempts=0
:wait_backend
timeout /t 3 /nobreak >nul
set /a attempts+=1
powershell -NoProfile -Command "try{Invoke-WebRequest -UseBasicParsing '%BACKEND_URL%' -TimeoutSec 2|Out-Null;exit 0}catch{exit 1}" >nul 2>nul
if not errorlevel 1 goto backend_ok
if %attempts% lss 30 goto wait_backend
echo [ERROR] Backend did not start. Is port 8000 blocked?
pause & exit /b 1
:backend_ok
echo [OK] Backend is running on http://127.0.0.1:8000

:: ── Start Frontend in background within this same window ──
echo.
echo [2/2] Starting Frontend on port 3000...
start /b cmd /c "%TEMP%\rs_frontend.cmd"

:: ── Wait for frontend ──
echo Waiting for Frontend to start...
set /a attempts=0
:wait_frontend
timeout /t 4 /nobreak >nul
set /a attempts+=1
powershell -NoProfile -Command "try{Invoke-WebRequest -UseBasicParsing '%FRONTEND_URL%' -TimeoutSec 2|Out-Null;exit 0}catch{exit 1}" >nul 2>nul
if not errorlevel 1 goto frontend_ok
if %attempts% lss 30 goto wait_frontend
echo [ERROR] Frontend did not start. Is port 3000 blocked?
pause & exit /b 1
:frontend_ok
echo [OK] Frontend is running on http://127.0.0.1:3000

:: ── Open browser automatically ──
echo.
echo Opening RiskShield AI Manager in browser...
start http://127.0.0.1:3000

echo.
echo =====================================================
echo   RiskShield AI is live!
echo   http://127.0.0.1:3000
echo   Press Ctrl+C to stop all services.
echo =====================================================
echo.

:: Keep this window alive so processes keep running
:loop
timeout /t 60 /nobreak >nul
goto loop
