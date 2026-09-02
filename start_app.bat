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

:: Kill anything already on port 8000 or 3000 so we start clean
echo Freeing ports 8000 and 3000...
for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":8000 " 2^>nul') do (
  taskkill /PID %%P /F >nul 2>nul
)
for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":3000 " 2^>nul') do (
  taskkill /PID %%P /F >nul 2>nul
)
timeout /t 2 /nobreak >nul

:: Check backend venv
if not exist "%ROOT%backend\.venv\Scripts\python.exe" (
  echo [!] Backend environment not found. Running install.bat first...
  call "%ROOT%install.bat"
  if errorlevel 1 (
    echo [ERROR] Installation failed.
    pause
    exit /b 1
  )
)

:: Check frontend node_modules
if not exist "%ROOT%frontend\node_modules\.bin\next.cmd" (
  echo [!] Frontend dependencies not found. Running install.bat first...
  call "%ROOT%install.bat"
  if errorlevel 1 (
    echo [ERROR] Installation failed.
    pause
    exit /b 1
  )
)

:: Resolve npm path
set "NPM_CMD=npm"
where npm >nul 2>nul
if errorlevel 1 (
  if exist "%ProgramFiles%\nodejs\npm.cmd" set "NPM_CMD=%ProgramFiles%\nodejs\npm.cmd"
)

:: Start Ollama only if not already running on port 11434
netstat -ano | findstr ":11434 " >nul 2>nul
if errorlevel 1 (
  set "OLLAMA_EXE="
  where ollama >nul 2>nul && set "OLLAMA_EXE=ollama"
  if not defined OLLAMA_EXE (
    if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" set "OLLAMA_EXE=%LOCALAPPDATA%\Programs\Ollama\ollama.exe"
  )
  if defined OLLAMA_EXE (
    echo Starting Ollama AI server...
    start /b "" "%OLLAMA_EXE%" serve
    timeout /t 3 /nobreak >nul
  )
) else (
  echo Ollama already running on port 11434 - skipping.
)

:: Write backend launcher script to avoid nested quote issues
set "BACK_DIR=%ROOT%backend"
set "BACK_PY=%ROOT%backend\.venv\Scripts\python.exe"
set "FRONT_DIR=%ROOT%frontend"

:: Start Backend using a helper approach - write to temp cmd file
echo @echo off > "%TEMP%\riskshield_backend.cmd"
echo cd /d "%BACK_DIR%" >> "%TEMP%\riskshield_backend.cmd"
echo call ".venv\Scripts\activate.bat" >> "%TEMP%\riskshield_backend.cmd"
echo python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 >> "%TEMP%\riskshield_backend.cmd"
echo pause >> "%TEMP%\riskshield_backend.cmd"

echo @echo off > "%TEMP%\riskshield_frontend.cmd"
echo cd /d "%FRONT_DIR%" >> "%TEMP%\riskshield_frontend.cmd"
echo "%NPM_CMD%" run dev -- -H 127.0.0.1 -p 3000 >> "%TEMP%\riskshield_frontend.cmd"
echo pause >> "%TEMP%\riskshield_frontend.cmd"

echo [1/2] Starting Backend on port 8000...
start "RiskShield Backend" cmd /c "%TEMP%\riskshield_backend.cmd"

echo [2/2] Starting Frontend on port 3000...
start "RiskShield Frontend" cmd /c "%TEMP%\riskshield_frontend.cmd"

echo.
echo Waiting for services to start...

:: Wait for backend
set /a attempts=0
:wait_backend
timeout /t 4 /nobreak >nul
set /a attempts+=1
powershell -NoProfile -Command "try{Invoke-WebRequest -UseBasicParsing '%BACKEND_URL%' -TimeoutSec 2|Out-Null;exit 0}catch{exit 1}" >nul 2>nul
if not errorlevel 1 goto backend_ok
if %attempts% lss 30 goto wait_backend
echo [WARNING] Backend taking long. Check the Backend window for errors.
goto open_browser
:backend_ok
echo   [OK] Backend is running!

:: Wait for frontend
set /a attempts=0
:wait_frontend
timeout /t 4 /nobreak >nul
set /a attempts+=1
powershell -NoProfile -Command "try{Invoke-WebRequest -UseBasicParsing '%FRONTEND_URL%' -TimeoutSec 2|Out-Null;exit 0}catch{exit 1}" >nul 2>nul
if not errorlevel 1 goto frontend_ok
if %attempts% lss 30 goto wait_frontend
echo [WARNING] Frontend taking long. Check the Frontend window for errors.
goto open_browser
:frontend_ok
echo   [OK] Frontend is running!

:open_browser
echo.
echo Opening RiskShield AI Manager...
start http://127.0.0.1:3000

echo.
echo =====================================================
echo   RiskShield AI is running!
echo   Backend:  http://127.0.0.1:8000
echo   Frontend: http://127.0.0.1:3000
echo   Close the Backend/Frontend windows to stop.
echo =====================================================
echo.
pause
