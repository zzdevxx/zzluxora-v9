; ZZLUXORA v9 — Inno Setup installer (M8 Task 8.3, D6)
; Build EXE dulu: python build.py --noconsole
; Lalu compile:   ISCC.exe installer.iss

#define MyAppName "ZZLUXORA"
#define MyAppVersion "9.0.0"
#define MyAppPublisher "Andreas Restuawanta Christwara"
#define MyAppExeName "ZZLUXORA.exe"

[Setup]
AppId={{8E1B2E3C-5F0D-4A6B-9C7E-2F0D4A6B9C7E}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\ZZLUXORA
DefaultGroupName=ZZLUXORA
UninstallDisplayIcon={app}\{#MyAppExeName}
OutputDir=installer
OutputBaseFilename=ZZLUXORA-Setup-v9.0.0
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
; Data di AppData (R3 §21) — tidak diinstall ke Program Files
PrivilegesRequired=lowest

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
