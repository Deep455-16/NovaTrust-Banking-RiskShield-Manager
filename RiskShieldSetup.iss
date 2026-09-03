[Setup]
AppName=RiskShield AI Manager
AppVersion=2.0
AppPublisher=NovaTrust Banking
DefaultGroupName=RiskShield AI Manager

; Install into Local AppData - no Admin rights required
DefaultDirName={localappdata}\RiskShieldAI
PrivilegesRequired=lowest

; Output
OutputDir=.\Installer
OutputBaseFilename=RiskShieldSetup
Compression=lzma2
SolidCompression=yes
SetupIconFile=compiler:SetupClassicIcon.ico

; UI settings
WizardStyle=modern
ShowLanguageDialog=no
DisableDirPage=yes
DisableProgramGroupPage=yes

; Show a clear progress page for long installs
ShowComponentSizes=no
AlwaysShowComponentsList=no

[Messages]
WelcomeLabel1=Welcome to RiskShield AI Manager Setup
WelcomeLabel2=This installer will set up RiskShield AI Manager on your PC.%n%nIt will automatically install:%n  - Python 3.11 (backend runtime)%n  - Node.js 20 LTS (frontend runtime)%n  - Ollama AI Runtime (AI Copilot)%n  - All application dependencies%n%nThe first-time setup may take 10-20 minutes depending on your internet speed. Please keep this window open.

[Files]
; ===== Core application files =====
Source: "RiskShieldAI.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "install.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "start_app.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

; Backend source (venv built fresh on target machine)
Source: "backend\*"; DestDir: "{app}\backend"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: ".venv\*,__pycache__\*,*.pyc,*.pyo"

; Frontend source (node_modules installed fresh on target machine)
Source: "frontend\*"; DestDir: "{app}\frontend"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "node_modules\*,.next\*"

; Datasets
Source: "data\*"; DestDir: "{app}\data"; Flags: ignoreversion recursesubdirs createallsubdirs

; ===== Bundled installers (embedded directly in .exe) =====
; Place these files in the bundled\ folder before compiling with Inno Setup.
; Run bundled\download_deps.bat to download them automatically.
Source: "bundled\python-3.11.9-amd64.exe"; DestDir: "{app}\bundled"; Flags: ignoreversion; Check: FileExists(ExpandConstant('{src}\bundled\python-3.11.9-amd64.exe'))
Source: "bundled\node-v20.18.0-x64.msi"; DestDir: "{app}\bundled"; Flags: ignoreversion; Check: FileExists(ExpandConstant('{src}\bundled\node-v20.18.0-x64.msi'))
Source: "bundled\OllamaSetup.exe"; DestDir: "{app}\bundled"; Flags: ignoreversion; Check: FileExists(ExpandConstant('{src}\bundled\OllamaSetup.exe'))

[Icons]
Name: "{userdesktop}\RiskShield AI Manager"; Filename: "{app}\RiskShieldAI.exe"; Comment: "Launch RiskShield AI Manager"
Name: "{group}\RiskShield AI Manager"; Filename: "{app}\RiskShieldAI.exe"; Comment: "Launch RiskShield AI Manager"
Name: "{group}\Uninstall RiskShield"; Filename: "{uninstallexe}"

[Run]
; Run install.bat hidden - installs Python, Node.js, Ollama, pip packages, npm packages
Filename: "{app}\install.bat"; StatusMsg: "Installing Python, Node.js, AI model and all dependencies... This may take 10-20 minutes. Please wait."; Flags: runhidden waituntilterminated

; Auto-launch app after install
Filename: "{app}\RiskShieldAI.exe"; Description: "Launch RiskShield AI Manager now"; Flags: nowait postinstall skipifsilent

[Code]
// Show a custom progress page with helpful instructions during the long install
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssInstall then
  begin
    WizardForm.StatusLabel.Caption := 'Installing dependencies... This takes 10-20 minutes on first run.';
  end;
end;
