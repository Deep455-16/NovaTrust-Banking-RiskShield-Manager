@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul 2>nul

set "ROOT=%~dp0"
echo.
echo =====================================================
echo   RiskShield AI Manager - Automated Setup
echo =====================================================
echo.

:: ─────────────────────────────────────────────────────
:: STEP 1 — Python
:: ─────────────────────────────────────────────────────
echo [1/5] Checking for Python 3.11+...
set "PYTHON_EXE="

:: Check common Python locations
for %%P in (python python3) do (
  for /f "delims=" %%V in ('where %%P 2^>nul') do (
    if not defined PYTHON_EXE (
      %%P --version >nul 2>nul && set "PYTHON_EXE=%%P"
    )
  )
)

:: Try py launcher
if not defined PYTHON_EXE (
  py -3.11 --version >nul 2>nul && set "PYTHON_EXE=py -3.11"
)

:: Try known install paths
if not defined PYTHON_EXE (
  if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
  )
)

:: Still not found — download and install silently
if not defined PYTHON_EXE (
  echo   Python not found. Downloading Python 3.11.8...
  powershell -NoProfile -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe' -OutFile '%TEMP%\python_installer.exe' -UseBasicParsing"
  echo   Installing Python silently...
  "%TEMP%\python_installer.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 Include_launcher=1
  :: Wait for install to complete
  timeout /t 10 /nobreak >nul
  set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
)

:: Verify Python works
"%PYTHON_EXE%" --version >nul 2>nul
if errorlevel 1 (
  echo   [ERROR] Python installation failed. Please install Python 3.11+ manually from https://python.org
  pause
  exit /b 1
)
echo   Python OK: 
"%PYTHON_EXE%" --version

:: ─────────────────────────────────────────────────────
:: STEP 2 — Node.js
:: ─────────────────────────────────────────────────────
echo.
echo [2/5] Checking for Node.js...
set "NPM_EXE="
set "NODE_PATH_ADDED="

:: Check standard PATH
where npm >nul 2>nul && set "NPM_EXE=npm"

:: Check known install paths if not on PATH
if not defined NPM_EXE (
  if exist "%ProgramFiles%\nodejs\npm.cmd" (
    set "NPM_EXE=%ProgramFiles%\nodejs\npm.cmd"
    set "PATH=%ProgramFiles%\nodejs;%PATH%"
    set "NODE_PATH_ADDED=1"
  )
)
if not defined NPM_EXE (
  if exist "%APPDATA%\nvm\nodejs\npm.cmd" (
    set "NPM_EXE=%APPDATA%\nvm\nodejs\npm.cmd"
  )
)

:: Still not found — download and install silently
if not defined NPM_EXE (
  echo   Node.js not found. Downloading Node.js 20 LTS...
  powershell -NoProfile -Command "Invoke-WebRequest -Uri 'https://nodejs.org/dist/v20.11.1/node-v20.11.1-x64.msi' -OutFile '%TEMP%\node_installer.msi' -UseBasicParsing"
  echo   Installing Node.js silently... (may take 2-3 minutes)
  msiexec /i "%TEMP%\node_installer.msi" /quiet /norestart ADDLOCAL=ALL
  :: Wait for installer to finish
  timeout /t 20 /nobreak >nul
  set "PATH=%ProgramFiles%\nodejs;%PATH%"
  set "NPM_EXE=%ProgramFiles%\nodejs\npm.cmd"
)

:: Verify npm works
call "%NPM_EXE%" --version >nul 2>nul
if errorlevel 1 (
  echo   [ERROR] Node.js installation failed. Please install Node.js 20+ manually from https://nodejs.org
  pause
  exit /b 1
)
echo   Node.js OK: 
call "%NPM_EXE%" --version

:: ─────────────────────────────────────────────────────
:: STEP 3 — Python Virtual Environment + pip install
:: ─────────────────────────────────────────────────────
echo.
echo [3/5] Setting up Python backend environment...

if not exist "%ROOT%backend\.venv\Scripts\python.exe" (
  echo   Creating virtual environment...
  "%PYTHON_EXE%" -m venv "%ROOT%backend\.venv"
  if errorlevel 1 (
    echo   [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
  )
)

set "VENV_PYTHON=%ROOT%backend\.venv\Scripts\python.exe"
set "VENV_PIP=%ROOT%backend\.venv\Scripts\pip.exe"

echo   Upgrading pip...
"%VENV_PYTHON%" -m pip install --upgrade pip --quiet
if errorlevel 1 (
  echo   [ERROR] pip upgrade failed.
  pause
  exit /b 1
)

echo   Installing backend dependencies from requirements.txt...
echo   (This may take 5-10 minutes for first-time install)
"%VENV_PYTHON%" -m pip install -r "%ROOT%backend\requirements.txt"
if errorlevel 1 (
  echo   [ERROR] pip install -r requirements.txt failed.
  pause
  exit /b 1
)
echo   Backend Python dependencies installed successfully.

:: ─────────────────────────────────────────────────────
:: STEP 4 — Frontend npm install
:: ─────────────────────────────────────────────────────
echo.
echo [4/5] Installing frontend dependencies (Next.js + React)...
echo   (This may take 3-5 minutes for first-time install)

cd /d "%ROOT%frontend"
call "%NPM_EXE%" install --prefer-offline
if errorlevel 1 (
  echo   [ERROR] npm install failed. Retrying with clean cache...
  call "%NPM_EXE%" cache clean --force
  call "%NPM_EXE%" install
  if errorlevel 1 (
    echo   [ERROR] Frontend npm install failed completely.
    pause
    exit /b 1
  )
)

:: Verify next.js binary exists
if not exist "%ROOT%frontend\node_modules\.bin\next.cmd" (
  echo   [ERROR] Next.js was not found in node_modules after npm install.
  echo   Attempting to install Next.js directly...
  call "%NPM_EXE%" install next react react-dom
  if errorlevel 1 (
    pause
    exit /b 1
  )
)
echo   Frontend dependencies installed successfully.

:: ─────────────────────────────────────────────────────
:: STEP 5 — Ollama + Zephyr
:: ─────────────────────────────────────────────────────
echo.
echo [5/5] Checking for Ollama AI Runtime...
set "OLLAMA_EXE="

where ollama >nul 2>nul && set "OLLAMA_EXE=ollama"

if not defined OLLAMA_EXE (
  if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" (
    set "OLLAMA_EXE=%LOCALAPPDATA%\Programs\Ollama\ollama.exe"
    set "PATH=%LOCALAPPDATA%\Programs\Ollama;%PATH%"
  )
)

if not defined OLLAMA_EXE (
  echo   Ollama not found. Downloading Ollama...
  powershell -NoProfile -Command "Invoke-WebRequest -Uri 'https://ollama.com/download/OllamaSetup.exe' -OutFile '%TEMP%\OllamaSetup.exe' -UseBasicParsing"
  echo   Installing Ollama silently...
  "%TEMP%\OllamaSetup.exe" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART
  timeout /t 15 /nobreak >nul
  set "OLLAMA_EXE=%LOCALAPPDATA%\Programs\Ollama\ollama.exe"
  set "PATH=%LOCALAPPDATA%\Programs\Ollama;%PATH%"
)

:: Start ollama server in background and pull zephyr
echo   Starting Ollama server...
start /b "" "%OLLAMA_EXE%" serve
timeout /t 5 /nobreak >nul

echo   Pulling Zephyr 7B AI model (this may take 10-20 min on first run)...
"%OLLAMA_EXE%" pull zephyr:7b-beta
echo   AI Copilot model ready.

:: ─────────────────────────────────────────────────────
:: Done
:: ─────────────────────────────────────────────────────
echo.
echo =====================================================
echo   Installation Complete!
echo   Run start_app.bat to launch RiskShield AI Manager
echo =====================================================
echo.
exit /b 0
