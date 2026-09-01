@echo off
setlocal EnableExtensions

set "ROOT=%~dp0"
set "PYTHON_CMD=python"
echo Installing RiskShield AI Manager dependencies...

where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found on PATH. Install Python 3.11+ and run this file again.
  exit /b 1
)

where py >nul 2>nul
if not errorlevel 1 (
  py -3.11 -c "import sys" >nul 2>nul
  if not errorlevel 1 set "PYTHON_CMD=py -3.11"
)

where npm >nul 2>nul
if errorlevel 1 (
  echo npm was not found on PATH. Install Node.js 20+ and run this file again.
  exit /b 1
)

if not exist "%ROOT%backend\.venv\Scripts\python.exe" (
  echo Creating backend virtual environment...
  %PYTHON_CMD% -m venv "%ROOT%backend\.venv"
)

call "%ROOT%backend\.venv\Scripts\python.exe" --version >nul 2>nul
if errorlevel 1 (
  echo Rebuilding backend virtual environment...
  %PYTHON_CMD% -m venv "%ROOT%backend\.venv" --clear
)

echo Installing backend dependencies...
call "%ROOT%backend\.venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 exit /b 1

call "%ROOT%backend\.venv\Scripts\python.exe" -m pip install -r "%ROOT%backend\requirements.txt"
if errorlevel 1 exit /b 1

echo Installing frontend dependencies...
cd /d "%ROOT%frontend"
call npm install
if errorlevel 1 exit /b 1

echo Checking for optional AI Copilot dependencies (Ollama)...
where ollama >nul 2>nul
if not errorlevel 1 (
  echo Ollama found. Ensuring zephyr:7b-beta model is pulled...
  start /b cmd /c "ollama serve >nul 2>nul"
  timeout /t 2 /nobreak >nul
  call ollama pull zephyr:7b-beta
  echo AI Copilot setup complete.
) else (
  echo Ollama not found. Skipping optional AI Copilot setup.
)

echo.
echo Installation completed successfully.
echo Run start_app.bat to launch RiskShield AI Manager.
exit /b 0
