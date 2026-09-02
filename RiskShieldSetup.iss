[Setup]
; App Information
AppName=RiskShield AI Manager
AppVersion=1.0
AppPublisher=NovaTrust Banking
DefaultGroupName=RiskShield AI Manager

; Install into Local AppData — no Admin rights needed, npm install and pip install work fine here
DefaultDirName={localappdata}\RiskShieldAI
PrivilegesRequired=lowest

; Output settings
OutputDir=.\Installer
OutputBaseFilename=RiskShieldSetup
Compression=lzma2
SolidCompression=yes
SetupIconFile=compiler:SetupClassicIcon.ico

[Files]
; Root launchers and scripts
Source: "RiskShieldAI.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "install.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "start_app.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

; Backend — exclude .venv and pycache (install.bat builds them fresh on target machine)
Source: "backend\*"; DestDir: "{app}\backend"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: ".venv\*,__pycache__\*,*.pyc"

; Frontend — exclude node_modules and .next builds (npm install runs fresh on target machine)
Source: "frontend\*"; DestDir: "{app}\frontend"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "node_modules\*,.next\*"

; Data / datasets
Source: "data\*"; DestDir: "{app}\data"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Desktop shortcut
Name: "{userdesktop}\RiskShield AI Manager"; Filename: "{app}\RiskShieldAI.exe"; Comment: "Launch RiskShield AI Manager"
; Start Menu shortcut
Name: "{group}\RiskShield AI Manager"; Filename: "{app}\RiskShieldAI.exe"; Comment: "Launch RiskShield AI Manager"

[Run]
; STEP 1: Run install.bat completely hidden — downloads Python, Node, Ollama, pip packages, npm packages
Filename: "{app}\install.bat"; Description: "Setting up dependencies (Python, Node.js, AI model — takes 5-20 min)"; StatusMsg: "Installing Python, Node.js, AI model & all dependencies... Please wait (5-20 minutes)"; Flags: runhidden waituntilterminated

; STEP 2: Auto-launch the application after install finishes
Filename: "{app}\RiskShieldAI.exe"; Description: "Launch RiskShield AI Manager"; Flags: nowait postinstall skipifsilent
