; Définition des constantes
!define APPNAME "Game Launcher"
!define COMPANYNAME "GameLauncher"
!define DESCRIPTION "Un launcher de jeux personnalisé"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define INSTALLSIZE 57000

; Informations sur l'installateur
Name "${APPNAME}"
OutFile "GameLauncherSetup.exe"
InstallDir "$PROGRAMFILES\${COMPANYNAME}\${APPNAME}"
InstallDirRegKey HKCU "Software\${COMPANYNAME}\${APPNAME}" ""

; Demander les privilèges d'administrateur
RequestExecutionLevel admin

; Pages de l'installateur
!include "MUI2.nsh"
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "French"

; Installation principale
Section "Installation principale" SecDummy
    SetOutPath "$INSTDIR"
    
    ; Fichiers à installer
    File "dist\lanucher.exe"
    
    ; Créer un raccourci dans le menu démarrer
    CreateDirectory "$SMPROGRAMS\${COMPANYNAME}"
    CreateShortCut "$SMPROGRAMS\${COMPANYNAME}\${APPNAME}.lnk" "$INSTDIR\lanucher.exe"
    CreateShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\lanucher.exe"
    
    ; Écrire les informations de désinstallation
    WriteUninstaller "$INSTDIR\uninstall.exe"
    
    ; Écrire les informations dans le registre
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "DisplayIcon" "$\"$INSTDIR\lanucher.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "EstimatedSize" ${INSTALLSIZE}
SectionEnd

; Désinstallation
Section "Uninstall"
    ; Supprimer les fichiers
    Delete "$INSTDIR\lanucher.exe"
    Delete "$INSTDIR\uninstall.exe"
    
    ; Supprimer les raccourcis
    Delete "$SMPROGRAMS\${COMPANYNAME}\${APPNAME}.lnk"
    Delete "$DESKTOP\${APPNAME}.lnk"
    RMDir "$SMPROGRAMS\${COMPANYNAME}"
    
    ; Supprimer le dossier d'installation
    RMDir "$INSTDIR"
    
    ; Supprimer les entrées de registre
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}"
SectionEnd 