@echo off
setlocal EnableExtensions

set "ROOT=%~dp0"
set "BACKEND_URL=http://127.0.0.1:8000/api/v1/health"
set "FRONTEND_URL=http://127.0.0.1:3000"

if not exist "%ROOT%backend\.venv\Scripts\python.exe" (
  echo Backend virtual environment was not found. Run install.bat first.
  pause
  exit /b 1
)

if not exist "%ROOT%frontend\node_modules" (
  echo Frontend dependencies were not found. Run install.bat first.
  pause
  exit /b 1
)

echo ===================================================
echo Starting RiskShield AI Manager...
echo ===================================================
echo.

echo [1/2] Starting RiskShield Backend API (Port 8000)...
start /b cmd /c "cd /d "%ROOT%backend" && call ".venv\Scripts\activate.bat" && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

echo.
echo [2/2] Starting RiskShield Frontend UI (Port 3000)...
start /b cmd /c "cd /d "%ROOT%frontend" && npm run dev -- -H 127.0.0.1 -p 3000"

echo.
echo Waiting for services to become ready... (This may take up to 2 minutes as ML models load)

powershell -NoProfile -ExecutionPolicy Bypass -Command "$deadline=(Get-Date).AddSeconds(120); do { try { $r=Invoke-WebRequest -UseBasicParsing '%BACKEND_URL%' -TimeoutSec 2; if ($r.StatusCode -eq 200) { exit 0 } } catch {} Start-Sleep -Seconds 2 } while ((Get-Date) -lt $deadline); exit 1"
if errorlevel 1 (
  echo [ERROR] Backend did not become ready in time. Check the logs above.
  pause
  exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -Command "$deadline=(Get-Date).AddSeconds(120); do { try { $r=Invoke-WebRequest -UseBasicParsing '%FRONTEND_URL%' -TimeoutSec 2; if ($r.StatusCode -eq 200) { exit 0 } } catch {} Start-Sleep -Seconds 2 } while ((Get-Date) -lt $deadline); exit 1"
if errorlevel 1 (
  echo [ERROR] Frontend did not become ready in time. Check the logs above.
  pause
  exit /b 1
)

echo.
echo All services are running! Opening browser...
start http://127.0.0.1:3000

echo.
echo ===================================================
echo RiskShield AI Manager is running in this window. 
echo Keep this window open to keep the server running.
echo Press Ctrl+C to stop all services and exit.
echo ===================================================

:: Keep window open
:loop
timeout /t 3600 >nul
goto loop
