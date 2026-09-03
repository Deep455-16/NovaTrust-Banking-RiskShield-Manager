#define PythonBundled FileExists(SourcePath + "bundled\python-3.11.9-amd64.exe")
#define NodeBundled   FileExists(SourcePath + "bundled\node-v20.18.0-x64.msi")
#define OllamaBundled FileExists(SourcePath + "bundled\OllamaSetup.exe")

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

[Messages]
WelcomeLabel1=Welcome to RiskShield AI Manager Setup
WelcomeLabel2=This installer will set up RiskShield AI Manager on your PC.%n%nIt will automatically install:%n  - Python 3.11 (backend runtime)%n  - Node.js 20 LTS (frontend runtime)%n  - Ollama AI Runtime (AI Copilot)%n  - All application dependencies%n%nFirst-time setup may take 10-20 minutes. Please keep this window open.

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

; ===== Bundled installers (only included if present in bundled\ folder) =====
; To include these: run bundled\download_deps.bat BEFORE compiling
#if PythonBundled
Source: "bundled\python-3.11.9-amd64.exe"; DestDir: "{app}\bundled"; Flags: ignoreversion
#endif
#if NodeBundled
Source: "bundled\node-v20.18.0-x64.msi"; DestDir: "{app}\bundled"; Flags: ignoreversion
#endif
#if OllamaBundled
Source: "bundled\OllamaSetup.exe"; DestDir: "{app}\bundled"; Flags: ignoreversion
#endif

[Icons]
Name: "{userdesktop}\RiskShield AI Manager"; Filename: "{app}\RiskShieldAI.exe"; Comment: "Launch RiskShield AI Manager"
Name: "{group}\RiskShield AI Manager"; Filename: "{app}\RiskShieldAI.exe"; Comment: "Launch RiskShield AI Manager"
Name: "{group}\Uninstall RiskShield"; Filename: "{uninstallexe}"

[Run]
; Run install.bat hidden - installs Python, Node.js, Ollama, pip packages, npm packages
Filename: "{app}\install.bat"; StatusMsg: "Installing Python, Node.js, Ollama and all dependencies... This may take 10-20 minutes. Please wait."; Flags: runhidden waituntilterminated

; Auto-launch app after install finishes
Filename: "{app}\RiskShieldAI.exe"; Description: "Launch RiskShield AI Manager now"; Flags: nowait postinstall skipifsilent

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssInstall then
  begin
    WizardForm.StatusLabel.Caption := 'Installing... This takes 10-20 minutes on first run. Please wait.';
  end;
end;
