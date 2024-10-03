[Setup]
; Información del instalador
AppName=ScrapTool
AppVersion=1.0
AppPublisher=Pablo Álvaro Hidalgo
AppCopyright=© 2024 Pablo Álvaro Hidalgo. Todos los derechos reservados.
DefaultDirName={pf}\ScrapTool
DefaultGroupName=ScrapTool
OutputBaseFilename=ScrapToolInstaller
SetupIconFile=D:\APPS\ScrapTools\ScrapTool\Config\exeicon.ico
Compression=lzma
SolidCompression=yes
DisableDirPage=no

[Files]
; Incluir todos los archivos y carpetas dentro de "ScrapTool"
Source: "D:\APPS\ScrapTools\ScrapTool\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Crear acceso directo en el escritorio
Name: "{userdesktop}\ScrapTool"; Filename: "{app}\run_scraptool.bat"; IconFilename: "{app}\Config\exeicon.ico"; WorkingDir: "{app}"

[Run]
; Opcional: Ejecutar el programa después de la instalación
Filename: "{app}\run_scraptool.bat"; Description: "{cm:LaunchProgram, ScrapTool}"; Flags: nowait postinstall skipifsilent
