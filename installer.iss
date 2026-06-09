; Inno Setup Script for PortKiller

[Setup]
AppName=PortKiller
AppVersion=1.0.0
AppPublisher=QingMings

DefaultDirName={pf}\PortKiller
DefaultGroupName=PortKiller
UninstallDisplayIcon={app}\PortKiller.exe
Compression=lzma2
SolidCompression=yes
OutputDir=output
OutputBaseFilename=PortKiller-Setup

[Icons]
Name: "{group}\PortKiller"; Filename: "{app}\PortKiller.exe"; IconFilename: "{app}\app.ico"
Name: "{commondesktop}\PortKiller"; Filename: "{app}\PortKiller.exe"; IconFilename: "{app}\app.ico"

[Files]
Source: "dist\PortKiller\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Run]
Filename: "{app}\PortKiller.exe"; Description: "Launch PortKiller"; Flags: postinstall nowait skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"