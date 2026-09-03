@echo off
echo.
echo =====================================================
echo   RiskShield - Downloading Bundled Installers
echo =====================================================
echo.
echo This downloads Python, Node.js, and Ollama installers
echo into the bundled\ folder so they can be embedded
echo directly inside RiskShieldSetup.exe
echo.
echo Estimated download: ~110 MB total
echo.

set "BUNDLED=%~dp0"

echo [1/3] Downloading Python 3.11.9 (~27 MB)...
powershell -NoProfile -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile '%BUNDLED%python-3.11.9-amd64.exe' -UseBasicParsing"
if exist "%BUNDLED%python-3.11.9-amd64.exe" (
  echo   Python installer downloaded OK.
) else (
  echo   [ERROR] Python download failed.
)

echo.
echo [2/3] Downloading Node.js 20.18.0 LTS (~33 MB)...
powershell -NoProfile -Command "Invoke-WebRequest -Uri 'https://nodejs.org/dist/v20.18.0/node-v20.18.0-x64.msi' -OutFile '%BUNDLED%node-v20.18.0-x64.msi' -UseBasicParsing"
if exist "%BUNDLED%node-v20.18.0-x64.msi" (
  echo   Node.js installer downloaded OK.
) else (
  echo   [ERROR] Node.js download failed.
)

echo.
echo [3/3] Downloading Ollama (~55 MB)...
powershell -NoProfile -Command "Invoke-WebRequest -Uri 'https://ollama.com/download/OllamaSetup.exe' -OutFile '%BUNDLED%OllamaSetup.exe' -UseBasicParsing"
if exist "%BUNDLED%OllamaSetup.exe" (
  echo   Ollama installer downloaded OK.
) else (
  echo   [ERROR] Ollama download failed.
)

echo.
echo =====================================================
echo   Download complete. Now compile RiskShieldSetup.iss
echo   with Inno Setup to create the full installer.
echo =====================================================
echo.
pause
