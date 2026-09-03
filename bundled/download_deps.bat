@echo off
echo.
echo =====================================================
echo   RiskShield - Downloading Bundled Installers
echo =====================================================
echo.
echo This downloads Python, Node.js, and Ollama installers
echo into the bundled\ folder using high-speed curl.
echo.
echo Estimated download: ~165 MB total
echo.

set "BUNDLED=%~dp0"

echo [1/3] Downloading Python 3.11.9 (~27 MB)...
curl.exe -L --progress-bar -o "%BUNDLED%python-3.11.9-amd64.exe" "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
if exist "%BUNDLED%python-3.11.9-amd64.exe" (
  echo   Python installer downloaded OK.
) else (
  echo   [ERROR] Python download failed.
)

echo.
echo [2/3] Downloading Node.js 20.18.0 LTS (~33 MB)...
curl.exe -L --progress-bar -o "%BUNDLED%node-v20.18.0-x64.msi" "https://nodejs.org/dist/v20.18.0/node-v20.18.0-x64.msi"
if exist "%BUNDLED%node-v20.18.0-x64.msi" (
  echo   Node.js installer downloaded OK.
) else (
  echo   [ERROR] Node.js download failed.
)

echo.
echo [3/3] Downloading Ollama (~105 MB)...
curl.exe -L --progress-bar -o "%BUNDLED%OllamaSetup.exe" "https://ollama.com/download/OllamaSetup.exe"
if exist "%BUNDLED%OllamaSetup.exe" (
  echo   Ollama installer downloaded OK.
) else (
  echo   [ERROR] Ollama download failed.
)

echo.
echo =====================================================
echo   Download complete! All 3 files are in bundled\
echo   Now open Inno Setup and compile RiskShieldSetup.iss
echo =====================================================
echo.
pause
