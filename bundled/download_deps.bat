@echo off
echo.
echo =====================================================
echo   RiskShield - Downloading Bundled Installers
echo =====================================================
echo.
echo This downloads Python and Node.js installers
echo into the bundled\ folder using high-speed curl.
echo.
echo Estimated download: ~60 MB total
echo.

set "BUNDLED=%~dp0"

echo [1/2] Downloading Python 3.11.9 (~27 MB)...
curl.exe -L --progress-bar -o "%BUNDLED%python-3.11.9-amd64.exe" "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
if exist "%BUNDLED%python-3.11.9-amd64.exe" (
  echo   Python installer downloaded OK.
) else (
  echo   [ERROR] Python download failed.
)

echo.
echo [2/2] Downloading Node.js 20.18.0 LTS (~33 MB)...
curl.exe -L --progress-bar -o "%BUNDLED%node-v20.18.0-x64.msi" "https://nodejs.org/dist/v20.18.0/node-v20.18.0-x64.msi"
if exist "%BUNDLED%node-v20.18.0-x64.msi" (
  echo   Node.js installer downloaded OK.
) else (
  echo   [ERROR] Node.js download failed.
)

echo.
echo =====================================================
echo   Download complete! Files are in bundled\
echo   Now open Inno Setup and compile RiskShieldSetup.iss
echo =====================================================
echo.
pause
