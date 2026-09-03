@echo off
setlocal EnableDelayedExpansion

set "ROOT=%~dp0"
set "BUNDLED=%ROOT%bundled"

echo.
echo =====================================================
echo   RiskShield AI Manager - Automated Setup
echo =====================================================
echo.

:: =====================================================
:: STEP 1 - Python 3.11
:: =====================================================
echo [1/5] Checking for Python 3.11+...
set "PYTHON_EXE="

for /f "delims=" %%P in ('where python 2^>nul') do (
  if not defined PYTHON_EXE set "PYTHON_EXE=%%P"
)
for /f "delims=" %%P in ('where python3 2^>nul') do (
  if not defined PYTHON_EXE set "PYTHON_EXE=%%P"
)

if not defined PYTHON_EXE (
  py -3.11 --version >nul 2>nul && set "PYTHON_EXE=py -3.11"
)
if not defined PYTHON_EXE (
  if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
  )
)
if not defined PYTHON_EXE (
  if exist "%ProgramFiles%\Python311\python.exe" (
    set "PYTHON_EXE=%ProgramFiles%\Python311\python.exe"
  )
)

if not defined PYTHON_EXE (
  echo   Python not found. Installing Python 3.11...
  if exist "%BUNDLED%\python-3.11.9-amd64.exe" (
    echo   Using bundled Python installer...
    "%BUNDLED%\python-3.11.9-amd64.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 Include_launcher=1
  ) else (
    echo   Downloading Python 3.11.9 from python.org...
    powershell -NoProfile -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile '%TEMP%\python_installer.exe' -UseBasicParsing"
    "%TEMP%\python_installer.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 Include_launcher=1
  )
  timeout /t 20 /nobreak >nul
  if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
  ) else if exist "%ProgramFiles%\Python311\python.exe" (
    set "PYTHON_EXE=%ProgramFiles%\Python311\python.exe"
  )
)

if not defined PYTHON_EXE (
  echo   [ERROR] Python could not be installed.
  echo   Please install Python 3.11 manually from: https://www.python.org/downloads/
  pause
  exit /b 1
)

"%PYTHON_EXE%" --version >nul 2>nul
if errorlevel 1 (
  echo   [ERROR] Python not working correctly.
  pause
  exit /b 1
)
echo   Python OK:
"%PYTHON_EXE%" --version

:: =====================================================
:: STEP 2 - Node.js 20 LTS
:: =====================================================
echo.
echo [2/5] Checking for Node.js...
set "NPM_CMD="

where npm >nul 2>nul && set "NPM_CMD=npm"
if not defined NPM_CMD (
  if exist "%ProgramFiles%\nodejs\npm.cmd" (
    set "NPM_CMD=%ProgramFiles%\nodejs\npm.cmd"
    set "PATH=%ProgramFiles%\nodejs;%PATH%"
  )
)
if not defined NPM_CMD (
  if exist "%ProgramFiles(x86)%\nodejs\npm.cmd" (
    set "NPM_CMD=%ProgramFiles(x86)%\nodejs\npm.cmd"
    set "PATH=%ProgramFiles(x86)%\nodejs;%PATH%"
  )
)
if not defined NPM_CMD (
  if exist "%APPDATA%\nvm\nodejs\npm.cmd" (
    set "NPM_CMD=%APPDATA%\nvm\nodejs\npm.cmd"
  )
)

if not defined NPM_CMD (
  echo   Node.js not found. Installing Node.js 20 LTS...
  if exist "%BUNDLED%\node-v20.18.0-x64.msi" (
    echo   Using bundled Node.js installer...
    msiexec /i "%BUNDLED%\node-v20.18.0-x64.msi" /quiet /norestart ADDLOCAL=ALL
  ) else (
    echo   Downloading Node.js 20 LTS...
    powershell -NoProfile -Command "Invoke-WebRequest -Uri 'https://nodejs.org/dist/v20.18.0/node-v20.18.0-x64.msi' -OutFile '%TEMP%\node_installer.msi' -UseBasicParsing"
    msiexec /i "%TEMP%\node_installer.msi" /quiet /norestart ADDLOCAL=ALL
  )
  :: Wait loop - check every 5s, max 60s
  set /a node_wait=0
  :wait_node
  timeout /t 5 /nobreak >nul
  set /a node_wait+=5
  if exist "%ProgramFiles%\nodejs\npm.cmd" goto node_found
  if !node_wait! lss 60 goto wait_node
  :node_found
  set "NPM_CMD=%ProgramFiles%\nodejs\npm.cmd"
  set "PATH=%ProgramFiles%\nodejs;%PATH%"
)

if not defined NPM_CMD (
  echo   [ERROR] Node.js could not be installed.
  echo   Please install Node.js 20 LTS manually from: https://nodejs.org/en/download
  pause
  exit /b 1
)

call "%NPM_CMD%" --version >nul 2>nul
if errorlevel 1 (
  echo   [ERROR] npm not working.
  pause
  exit /b 1
)
echo   Node.js OK - npm version:
call "%NPM_CMD%" --version

:: =====================================================
:: STEP 3 - Python virtual environment + pip install
:: =====================================================
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

echo   Installing backend dependencies (first run may take 5-10 min)...
"%VENV_PYTHON%" -m pip install -r "%ROOT%backend\requirements.txt"
if errorlevel 1 (
  echo   [ERROR] pip install failed. Check your internet connection.
  pause
  exit /b 1
)
echo   Backend dependencies installed.

:: =====================================================
:: STEP 4 - Frontend npm install
:: =====================================================
echo.
echo [4/5] Installing frontend dependencies (first run may take 3-5 min)...

cd /d "%ROOT%frontend"
call "%NPM_CMD%" install --prefer-offline
if errorlevel 1 (
  echo   npm install failed. Retrying...
  call "%NPM_CMD%" cache clean --force
  call "%NPM_CMD%" install
  if errorlevel 1 (
    echo   [ERROR] Frontend npm install failed.
    pause
    exit /b 1
  )
)

if not exist "%ROOT%frontend\node_modules\.bin\next.cmd" (
  echo   Installing Next.js directly...
  call "%NPM_CMD%" install next react react-dom
)
echo   Frontend dependencies installed.



:: =====================================================
:: Done
:: =====================================================
echo.
echo =====================================================
echo   Installation Complete!
echo   Run start_app.bat to launch RiskShield AI Manager
echo =====================================================
echo.
exit /b 0
