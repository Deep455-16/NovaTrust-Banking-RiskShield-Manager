@echo off
setlocal EnableDelayedExpansion

set "ROOT=%~dp0"
set "BACKEND_URL=http://127.0.0.1:8000/api/v1/health"
set "FRONTEND_URL=http://127.0.0.1:3000"

echo.
echo ===================================================
echo Starting RiskShield AI Manager...
echo ===================================================
echo.

:: Kill anything already on port 8000 or 3000
for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":8000 " 2^>nul') do taskkill /PID %%P /F >nul 2>nul
for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":3000 " 2^>nul') do taskkill /PID %%P /F >nul 2>nul
timeout /t 1 /nobreak >nul

:: Check backend venv
if not exist "%ROOT%backend\.venv\Scripts\python.exe" (
  echo [!] Backend not found. Running install.bat...
  call "%ROOT%install.bat"
  if errorlevel 1 ( echo [ERROR] Install failed. & pause & exit /b 1 )
)

:: Check frontend next binary
if not exist "%ROOT%frontend\node_modules\.bin\next.cmd" (
  echo [!] Frontend not found. Running install.bat...
  call "%ROOT%install.bat"
  if errorlevel 1 ( echo [ERROR] Install failed. & pause & exit /b 1 )
)

:: Start Ollama only if not already running
netstat -ano | findstr ":11434 " >nul 2>nul
if errorlevel 1 (
  set "OLLAMA_EXE="
  where ollama >nul 2>nul && set "OLLAMA_EXE=ollama"
  if not defined OLLAMA_EXE if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" set "OLLAMA_EXE=%LOCALAPPDATA%\Programs\Ollama\ollama.exe"
  if defined OLLAMA_EXE start /b "" "%OLLAMA_EXE%" serve
)

:: Write backend helper (avoids nested quote issues)
set "BACK_DIR=%ROOT%backend"
set "NEXT_CMD=%ROOT%frontend\node_modules\.bin\next.cmd"
set "FRONT_DIR=%ROOT%frontend"

echo @echo off > "%TEMP%\rs_backend.cmd"
echo cd /d "%BACK_DIR%" >> "%TEMP%\rs_backend.cmd"
echo call ".venv\Scripts\activate.bat" >> "%TEMP%\rs_backend.cmd"
echo python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 >> "%TEMP%\rs_backend.cmd"

:: Use next.cmd directly — avoids broken bundled npm inside node_modules
echo @echo off > "%TEMP%\rs_frontend.cmd"
echo cd /d "%FRONT_DIR%" >> "%TEMP%\rs_frontend.cmd"
echo "%NEXT_CMD%" dev -H 127.0.0.1 -p 3000 >> "%TEMP%\rs_frontend.cmd"

echo [1/2] Starting RiskShield Backend API (Port 8000)...
start /b cmd /c "%TEMP%\rs_backend.cmd"

echo.
echo [2/2] Starting RiskShield Frontend UI (Port 3000)...
start /b cmd /c "%TEMP%\rs_frontend.cmd"

echo.
echo Waiting for services to become ready... (This may take up to 2 minutes)
echo.

:: Wait for backend
set /a attempts=0
:wait_backend
timeout /t 3 /nobreak >nul
set /a attempts+=1
powershell -NoProfile -Command "try{Invoke-WebRequest -UseBasicParsing '%BACKEND_URL%' -TimeoutSec 2|Out-Null;exit 0}catch{exit 1}" >nul 2>nul
if not errorlevel 1 goto backend_ok
if %attempts% lss 40 goto wait_backend
echo [ERROR] Backend did not start. Is port 8000 blocked?
pause & exit /b 1
:backend_ok

:: Wait for frontend
set /a attempts=0
:wait_frontend
timeout /t 3 /nobreak >nul
set /a attempts+=1
powershell -NoProfile -Command "try{Invoke-WebRequest -UseBasicParsing '%FRONTEND_URL%' -TimeoutSec 2|Out-Null;exit 0}catch{exit 1}" >nul 2>nul
if not errorlevel 1 goto frontend_ok
if %attempts% lss 40 goto wait_frontend
echo [ERROR] Frontend did not start. Is port 3000 blocked?
pause & exit /b 1
:frontend_ok

echo All services are running! Opening browser...
start http://127.0.0.1:3000

echo.
echo ===================================================
echo RiskShield AI Manager is running in this window.
echo Keep this window open to keep the server running.
echo Press Ctrl+C to stop all services and exit.
echo ===================================================
echo.

:loop
timeout /t 3600 >nul
goto loop
