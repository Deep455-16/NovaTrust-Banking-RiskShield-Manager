[Setup]
; App Information
AppName=RiskShield AI Manager
AppVersion=1.0
AppPublisher=NovaTrust Banking
DefaultGroupName=RiskShield AI Manager

; Install into Local AppData so the app doesn't need Administrator privileges to download Python/Node dependencies via the launcher.
DefaultDirName={localappdata}\RiskShieldAI
PrivilegesRequired=lowest

; Output settings
OutputDir=.\Installer
OutputBaseFilename=RiskShieldSetup
Compression=lzma2
SolidCompression=yes
SetupIconFile=compiler:SetupClassicIcon.ico

[Files]
; Include the root executables and scripts
Source: "RiskShieldAI.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "start_app.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "install.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

; Include backend, but EXCLUDE .venv and pycache so the installer is tiny. The C# launcher handles this.
Source: "backend\*"; DestDir: "{app}\backend"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: ".venv\*,__pycache__\*"

; Include frontend, but EXCLUDE node_modules and .next builds.
Source: "frontend\*"; DestDir: "{app}\frontend"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "node_modules\*,.next\*"

; Include the dataset folder
Source: "data\*"; DestDir: "{app}\data"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Create a Desktop shortcut and Start Menu shortcut
Name: "{userdesktop}\RiskShield AI Manager"; Filename: "{app}\RiskShieldAI.exe"
Name: "{group}\RiskShield AI Manager"; Filename: "{app}\RiskShieldAI.exe"

[Run]
; Run install.bat to download dependencies completely hidden from the user, but update the installer text!
Filename: "{app}\install.bat"; Description: "Downloading Required Dependencies (Python, Node, AI)"; StatusMsg: "Downloading AI & App dependencies (this may take 5-10 minutes)..."; Flags: runhidden waituntilterminated
; Auto-launch the application when the installation finishes
Filename: "{app}\RiskShieldAI.exe"; Description: "Launch RiskShield AI Manager"; Flags: nowait postinstall skipifsilent
