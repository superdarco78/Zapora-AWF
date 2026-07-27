; ============================================================
;  ZAPORA-AWF — skrypt instalatora (Inno Setup 6)
;  Buduje: ZAPORA-AWF-Instalator-v4.8.exe
; ============================================================

#define NazwaApp      "ZAPORA-AWF"
#define WersjaApp     "4.8"
#define ProducentApp  "Akademia Wychowania Fizycznego w Warszawie"
#define StronaApp     "https://www.awf.edu.pl"
#define PlikExe       "ZAPORA-AWF.exe"

[Setup]
; Unikalny identyfikator — NIE zmieniaj przy kolejnych wersjach,
; dzieki temu nowa wersja nadpisze stara zamiast instalowac sie obok.
AppId={{8F3A61C4-2D9E-4B77-A5C1-7E0D93B4F218}
AppName={#NazwaApp}
AppVersion={#WersjaApp}
AppVerName={#NazwaApp} {#WersjaApp}
AppPublisher={#ProducentApp}
AppPublisherURL={#StronaApp}
AppSupportURL={#StronaApp}
VersionInfoVersion=4.8.0.0
VersionInfoCompany={#ProducentApp}
VersionInfoDescription=ZAPORA-AWF — kontrola wjazdu

; Instalacja dla biezacego uzytkownika — bez pytania o hasło administratora
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
DefaultDirName={autopf}\{#NazwaApp}
DefaultGroupName={#NazwaApp}
DisableProgramGroupPage=yes
AllowNoIcons=yes

OutputDir=.
OutputBaseFilename=ZAPORA-AWF-Instalator-v{#WersjaApp}
SetupIconFile=ikona.ico
UninstallDisplayIcon={app}\{#PlikExe}
UninstallDisplayName={#NazwaApp} {#WersjaApp}

; Windows 7 SP1 i nowsze; oficjalnie testowane na Windows 10 i 11
MinVersion=6.1sp1
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ShowLanguageDialog=no
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "polski"; MessagesFile: "compiler:Languages\Polish.isl"

[Tasks]
Name: "desktopicon"; Description: "Utworz skrot na pulpicie"; \
    GroupDescription: "Dodatkowe skroty:"; Flags: checkedonce
Name: "startupicon"; Description: "Uruchamiaj automatycznie przy starcie Windows"; \
    GroupDescription: "Dodatkowe skroty:"; Flags: unchecked

[Files]
; Cala zawartosc folderu zbudowanego przez PyInstaller (--onedir)
Source: "dist\ZAPORA-AWF\*"; DestDir: "{app}"; \
    Flags: ignoreversion recursesubdirs createallsubdirs
Source: "logo.png";  DestDir: "{app}"; Flags: ignoreversion
Source: "ikona.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "CZYTAJ-MNIE.md"; DestDir: "{app}"; DestName: "Instrukcja.txt"; Flags: ignoreversion isreadme

[Icons]
Name: "{group}\{#NazwaApp}";              Filename: "{app}\{#PlikExe}"
Name: "{group}\Instrukcja";               Filename: "{app}\Instrukcja.txt"
Name: "{group}\Odinstaluj {#NazwaApp}";   Filename: "{uninstallexe}"
Name: "{autodesktop}\{#NazwaApp}";        Filename: "{app}\{#PlikExe}"; Tasks: desktopicon
Name: "{userstartup}\{#NazwaApp}";        Filename: "{app}\{#PlikExe}"; Tasks: startupicon

[Run]
Filename: "{app}\{#PlikExe}"; Description: "Uruchom {#NazwaApp} teraz"; \
    Flags: nowait postinstall skipifsilent

[Messages]
polski.WelcomeLabel2=Ten kreator zainstaluje program [name/ver] na Twoim komputerze.%n%nPIN fabryczny: 1234 — zmien go po pierwszym uruchomieniu.%n%nZalecane jest zamkniecie innych aplikacji przed kontynuowaniem.

[Code]
// Przy odinstalowaniu pytamy, czy skasowac rowniez baze numerow i historie.
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  KatDanych: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    KatDanych := ExpandConstant('{userappdata}\ZAPORA-AWF');
    if DirExists(KatDanych) then
    begin
      if MsgBox('Usunac rowniez baze numerow i historie wjazdow?' + #13#10 + #13#10 +
                KatDanych + #13#10 + #13#10 +
                'Wybierz Nie, jesli planujesz zainstalowac program ponownie.',
                mbConfirmation, MB_YESNO) = IDYES then
        DelTree(KatDanych, True, True, True);
    end;
  end;
end;
