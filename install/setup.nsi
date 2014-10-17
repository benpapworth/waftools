!addplugindir "plugins"
!include "plugins\EnvVarUpdate.nsh"
!include "MUI2.nsh"
!include "x64.nsh"

!ifndef VER_MAJOR
!define VER_MAJOR			0
!endif
!ifndef VER_MINOR
!define VER_MINOR			0
!endif
!ifndef VER_PATCH
!define VER_PATCH			0
!endif

!define VERSION     		"${VER_MAJOR}.${VER_MINOR}.${VER_PATCH}"
!define REGKEY      		"Software\Waftools"
!define UNINSTALL_REGKEY	"Software\Microsoft\Windows\CurrentVersion\Uninstall\Waftools"

!ifndef PKG_NAME
!ifdef RunningX64
!define PKG_NAME			"waftools-win64-setup.exe"
!else
!define PKG_NAME			"waftools-win32-setup.exe"
!endif
!endif

!define PYTHON_MAJ			"3.4"
!define PYTHON_VER			"3.4.2"
!define WAF_VER				"1.8.2"
!define ECLIPSE_REL			"luna"
!define ECLIPSE_VER			"SR1"
!define CPPCHECK_VER		"1.64"
!define DOXYGEN_VER			"1.8.8"
!define NSIS_VER			"3.0a2"
!define INDENT_VER			"2.2.10"

!ifdef RunningX64
!define PYTHON_PKG			"python-${PYTHON_VER}.amd64.msi"
!else
!define PYTHON_PKG			"python-${PYTHON_VER}.msi"
!endif
!define WAF_PKG				"waf-${WAF_VER}.tar.bz2"
!define MINGW_PKG			"mingw-get-setup.exe"
!define CPPCHECK_PKG		"cppcheck-${CPPCHECK_VER}-x86-Setup.msi"
!define DOXYGEN_PKG			"doxygen-${DOXYGEN_VER}-setup.exe"
!define NSIS_PKG			"nsis-${NSIS_VER}-setup.exe"
!ifdef RunningX64
!define ECLIPSE_PKG			"eclipse-cpp-${ECLIPSE_REL}-${ECLIPSE_VER}-win32-x86_64.zip"
!else
!define ECLIPSE_PKG			"eclipse-cpp-${ECLIPSE_REL}-${ECLIPSE_VER}-win32.zip"
!endif
!define INDENT_PKG			"indent-{INDENT_VER}-setup.exe"


Name                    	"Waftools"
OutFile                 	"${PKG_NAME}"
InstallDir              	"C:\programs\waftools"
InstallDirRegKey        	HKCU "${REGKEY}" ""
RequestExecutionLevel   	admin
AutoCloseWindow         	false
ShowInstDetails         	show
ShowUnInstDetails       	show
CRCCheck                	On

!define MUI_ABORTWARNING
!define MUI_STARTMENUPAGE_REGISTRY_ROOT         HKCU
!define MUI_STARTMENUPAGE_REGISTRY_KEY          "${REGKEY}"
!define MUI_STARTMENUPAGE_REGISTRY_VALUENAME    "Start Menu Folder"  
!define MUI_VERSION                             "${VERSION}"
!define MUI_PRODUCT                             "Waftools"
!define MUI_BRANDINGTEXT                        "WAF Build tools and environment setup"

Var StartMenuFolder
Var InstallPath
Var UninstallString

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_STARTMENU Application $StartMenuFolder
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_COMPONENTS
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH
!insertmacro MUI_LANGUAGE "English"


Section "-Install" Section0
	SetOutPath "$INSTDIR"
	File extract.py
SectionEnd


Section /o "Python" Section1
	SetOutPath "$INSTDIR"
	NSISdl::download https://www.python.org/ftp/python/${PYTHON_VER}/${PYTHON_PKG} "${PYTHON_PKG}"
	ExecWait '"msiexec" /i "${PYTHON_PKG}"'
	
	${If} ${RunningX64}
		SetRegView 64
	${EndIf}
	ReadRegStr $R0 HKLM "SOFTWARE\Python\PythonCore\${PYTHON_MAJ}\InstallPath" ""
	StrCpy $InstallPath $R0
	StrCmp $InstallPath "" 0 +3
	ReadRegStr $R0 HKCU "SOFTWARE\Python\PythonCore\${PYTHON_MAJ}\InstallPath" ""
	StrCpy $InstallPath $R0
	StrCpy $0 $InstallPath "" -1
	StrCmp $0 "\" +2 0
	StrCmp $0 "/" 0 +2
	StrCpy $0 $InstallPath -1
	StrCpy $InstallPath $0
	${EnvVarUpdate} $0 "PATH" "R" "HKLM" "$InstallPath\Scripts"
	${EnvVarUpdate} $0 "PATH" "P" "HKLM" "$InstallPath\Scripts"
	${EnvVarUpdate} $0 "PATH" "R" "HKLM" "$InstallPath"
	${EnvVarUpdate} $0 "PATH" "P" "HKLM" "$InstallPath"

	ReadEnvStr $R0 "PATH"
	StrCpy $R0 "$InstallPath;$InstallPath\Scripts;$R0"
	SetEnv::SetEnvVar "PATH" $R0
SectionEnd
LangString DESC_Section1 ${LANG_ENGLISH} "Installs Python ${PYTHON_VER}."


Section /o "Build Tools" Section2
	SetOutPath "$INSTDIR"
	nsExec::ExecToLog 'python --version'
	Pop $0
	${If} $0 != 0
		MessageBox MB_OK "No suitable Python interpreter found, please install it first."
		Abort
	${EndIf}
	
	nsExec::ExecToLog 'pip install -I Pygments'
	Pop $0
	${If} $0 != 0
		MessageBox MB_OK "Failed to install Pygments."
		Abort
	${EndIf}

	nsExec::ExecToLog 'pip install -I waftools'
	Pop $0
	${If} $0 != 0
		MessageBox MB_OK "Failed to install waftools."
		Abort
	${EndIf}

	SetOutPath "$INSTDIR"
	NSISdl::download http://ftp.waf.io/pub/release/${WAF_PKG} "${WAF_PKG}"	
	DetailPrint "Extracting Waf build system..."
	nsExec::ExecToLog "python extract.py --name=${WAF_PKG} --path=$INSTDIR"
	Pop $0
	${If} $0 != 0
		MessageBox MB_OK "Failed to extract compressed archive."
		Abort
	${EndIf}
	
	${If} ${RunningX64}
		SetRegView 64
	${EndIf}
	${EnvVarUpdate} $0 "PATH" "R" "HKLM" "$INSTDIR\waf-${WAF_VER}"
	${EnvVarUpdate} $0 "PATH" "P" "HKLM" "$INSTDIR\waf-${WAF_VER}"
SectionEnd
LangString DESC_Section2 ${LANG_ENGLISH} "Installs required build tools and scripts (requires python)."


Section /o "MinGW" Section3
	SetOutPath "$INSTDIR"
	NSISdl::download http://heanet.dl.sourceforge.net/project/mingw/Installer/${MINGW_PKG} "${MINGW_PKG}"
	ExecWait "${MINGW_PKG}"

	${If} ${RunningX64}
		SetRegView 64
	${EndIf}
	${EnvVarUpdate} $0 "PATH" "R" "HKLM" "$INSTDIR\mingw\msys\1.0\bin"
	${EnvVarUpdate} $0 "PATH" "A" "HKLM" "$INSTDIR\mingw\msys\1.0\bin"
	${EnvVarUpdate} $0 "PATH" "R" "HKLM" "$INSTDIR\mingw\bin"
	${EnvVarUpdate} $0 "PATH" "A" "HKLM" "$INSTDIR\mingw\bin"
    CreateShortCut "$DESKTOP\MinGW Installer.lnk" "$INSTDIR\mingw\libexec\mingw-get\guimain.exe"
SectionEnd
LangString DESC_Section3 ${LANG_ENGLISH} "Installs MinGW Compiler and tools."


Section /o "Eclipse CDT" Section4
    SetOutPath "$INSTDIR"
	NSISdl::download http://ftp.snt.utwente.nl/pub/software/eclipse//technology/epp/downloads/release/${ECLIPSE_REL}/${ECLIPSE_VER}/${ECLIPSE_PKG} ${ECLIPSE_PKG}

	DetailPrint "Extracting Waf build system..."
	nsExec::ExecToLog "python extract.py --name=${WAF_PKG} --path=$INSTDIR\eclipse"
    CreateShortCut "$DESKTOP\Eclipse.lnk" "$INSTDIR\eclipse\eclipse.exe"
SectionEnd
LangString DESC_Section4 ${LANG_ENGLISH} "Install Eclipse CDT ${ECLIPSE_REL}-${ECLIPSE_VER}"


Section /o "CppCheck" Section5
    SetOutPath "$INSTDIR"
	NSISdl::download http://optimate.dl.sourceforge.net/project/cppcheck/cppcheck/${CPPCHECK_VER}/${CPPCHECK_PKG} "${CPPCHECK_PKG}"
    ExecWait '"msiexec" /i "${CPPCHECK_PKG}"'	

	${If} ${RunningX64}
		SetRegView 64
	${EndIf}
	ReadRegStr $R0 HKCU "Software\Cppcheck" "InstallationPath"
	StrCpy $InstallPath $R0
	StrCpy $0 $InstallPath "" -1
	StrCmp $0 "\" +2 0
	StrCmp $0 "/" 0 +2
	StrCpy $0 $InstallPath -1
	StrCpy $InstallPath $0
	${EnvVarUpdate} $0 "PATH" "R" "HKLM" "$InstallPath"
	${EnvVarUpdate} $0 "PATH" "A" "HKLM" "$InstallPath"
SectionEnd
LangString DESC_Section5 ${LANG_ENGLISH} "Installs CppCheck ${CPPCHECK_VER}"


Section /o "Doxygen" Section6
    SetOutPath "$INSTDIR"
	NSISdl::download http://ftp.stack.nl/pub/users/dimitri/${DOXYGEN_PKG} "${DOXYGEN_PKG}"
    ExecWait '"msiexec" /i "${DOXYGEN_PKG}"'	

	${If} ${RunningX64}
		SetRegView 64
	${EndIf}
	ReadRegStr $R0 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\doxygen_is1" "InstallLocation"
	StrCpy $InstallPath $R0
	StrCpy $0 $InstallPath "" -1
	StrCmp $0 "\" +2 0
	StrCmp $0 "/" 0 +2
	StrCpy $0 $InstallPath -1
	StrCpy $InstallPath $0
	${EnvVarUpdate} $0 "PATH" "R" "HKLM" "$InstallPath"
	${EnvVarUpdate} $0 "PATH" "A" "HKLM" "$InstallPath"
SectionEnd
LangString DESC_Section6 ${LANG_ENGLISH} "Installs Doxygen ${DOXYGEN_VER}"


Section /o "NSIS" Section7
    SetOutPath "$INSTDIR"
	NSISdl::download http://prdownloads.sourceforge.net/nsis/${NSIS_PKG}?download "${NSIS_PKG}"
	ExecWait "${NSIS_PKG}"

	${If} ${RunningX64}
		SetRegView 32
	${EndIf}
	ReadRegStr $R0 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\NSIS" "InstallLocation"
	StrCpy $InstallPath $R0
	${If} ${RunningX64}
		SetRegView 64
	${EndIf}
	${EnvVarUpdate} $0 "PATH" "R" "HKLM" "$InstallPath"
	${EnvVarUpdate} $0 "PATH" "A" "HKLM" "$InstallPath"	
SectionEnd
LangString DESC_Section7 ${LANG_ENGLISH} "Install NSIS ${NSIS_VER}"


Section /o "GNU indent" Section8
    SetOutPath "$INSTDIR"
	NSISdl::download http://freefr.dl.sourceforge.net/project/gnuwin32/indent/${INDENT_VER}/${INDENT_PKG} "${INDENT_PKG}"
	ExecWait "${INDENT_PKG}"
SectionEnd
LangString DESC_Section8 ${LANG_ENGLISH} "Install NSIS ${NSIS_VER}"


Section "-Post install" Section9
	${If} ${RunningX64}
		SetRegView 64
	${EndIf}
    WriteRegStr HKCU "${REGKEY}" 				"" 					$INSTDIR
    WriteRegStr HKCU "${UNINSTALL_REGKEY}" 		"DisplayName"		"Waftools"
    WriteRegStr HKCU "${UNINSTALL_REGKEY}" 		"DisplayVersion"	"${VERSION}"
    WriteRegStr HKCU "${UNINSTALL_REGKEY}" 		"InstallLocation"	"$INSTDIR"
    WriteRegStr HKCU "${UNINSTALL_REGKEY}" 		"Publisher"			""
    WriteRegStr HKCU "${UNINSTALL_REGKEY}" 		"UninstallString"	"$INSTDIR\Uninstall.exe"
	WriteRegDWORD HKCU "${UNINSTALL_REGKEY}"	"VersionMajor"		${VER_MAJOR}
	WriteRegDWORD HKCU "${UNINSTALL_REGKEY}"	"VersionMinor"		${VER_MINOR}
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    
    !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
        CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
        CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
    !insertmacro MUI_STARTMENU_WRITE_END
	
	SetRebootFlag true	
SectionEnd


!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
	!insertmacro MUI_DESCRIPTION_TEXT ${Section1} $(DESC_Section1)
	!insertmacro MUI_DESCRIPTION_TEXT ${Section2} $(DESC_Section2)
	!insertmacro MUI_DESCRIPTION_TEXT ${Section3} $(DESC_Section3)
	!insertmacro MUI_DESCRIPTION_TEXT ${Section4} $(DESC_Section4)
	!insertmacro MUI_DESCRIPTION_TEXT ${Section5} $(DESC_Section5)
	!insertmacro MUI_DESCRIPTION_TEXT ${Section6} $(DESC_Section6)
	!insertmacro MUI_DESCRIPTION_TEXT ${Section7} $(DESC_Section7)
	!insertmacro MUI_DESCRIPTION_TEXT ${Section8} $(DESC_Section8)
!insertmacro MUI_FUNCTION_DESCRIPTION_END


Section /o "Un.Python"
	${If} ${RunningX64}
		SetRegView 64
	${EndIf}
	ReadRegStr $R0 HKLM "SOFTWARE\Python\PythonCore\${PYTHON_MAJ}\InstallPath" ""
	StrCpy $InstallPath $R0
	StrCmp $InstallPath "" 0 +3
	ReadRegStr $R0 HKCU "SOFTWARE\Python\PythonCore\${PYTHON_MAJ}\InstallPath" ""
	StrCpy $InstallPath $R0
	StrCpy $0 $InstallPath "" -1
	StrCmp $0 "\" +2 0
	StrCmp $0 "/" 0 +2
	StrCpy $0 $InstallPath -1
	StrCpy $InstallPath $0
    ${un.EnvVarUpdate} $0 "PATH" "R" "HKLM" "$InstallPath\Scripts"

    ExecWait '"msiexec" /uninstall "$INSTDIR\packages\${PYTHON_PKG}"'
	RMDir /r $InstallPath
SectionEnd


Section /o "Un.Build Tools"
	RMDir /r "$INSTDIR\waf"
	
	${If} ${RunningX64}
		SetRegView 64
	${EndIf}
	${Un.EnvVarUpdate} $0 "PATH" "R" "HKLM" "$INSTDIR\waf"
SectionEnd


Section /o "Un.MinGW"
	RMDir /r "$INSTDIR\mingw"
	
	${If} ${RunningX64}
		SetRegView 64
	${EndIf}
	${Un.EnvVarUpdate} $0 "PATH" "R" "HKLM" "$INSTDIR\mingw\msys\1.0\bin"
	${Un.EnvVarUpdate} $0 "PATH" "R" "HKLM" "$INSTDIR\mingw\bin"
    Delete "$DESKTOP\MinGW Installer.lnk"
SectionEnd


Section /o "Un.Eclipse CDT"
	RMDir /r "$INSTDIR\eclipse"
	Delete "$DESKTOP\Eclipse.lnk"
SectionEnd


Section /o "Un.CppCheck"
	${If} ${RunningX64}
		SetRegView 64
	${EndIf}	
	ReadRegStr $R0 HKCU "SOFTWARE\CppCheck" "InstallationPath"
	StrCpy $InstallPath $R0
    ${un.EnvVarUpdate} $0 "PATH" "R" "HKLM" "$InstallPath"
    ExecWait '"msiexec" /uninstall "$INSTDIR\packages\${CPPCHECK_PKG}"'	
SectionEnd


Section /o "Un.Doxygen"
	${If} ${RunningX64}
		SetRegView 64
	${EndIf}	
	ReadRegStr $R0 HKCU "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\doxygen_is1" "InstallLocation"
	StrCpy $InstallPath $R0
    ${un.EnvVarUpdate} $0 "PATH" "R" "HKLM" "$InstallPath"
	
	ReadRegStr $R0 HKCU "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\doxygen_is1" "UninstallString"
    ExecWait $R0
SectionEnd


Section /o "Un.NSIS"
	${If} ${RunningX64}
		SetRegView 32
	${EndIf}
	ReadRegStr $R0 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\NSIS" "InstallLocation"
	StrCpy $InstallPath $R0
	ReadRegStr $R0 HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\NSIS" "UninstallString"
	StrCpy $UninstallString $R0

	${If} ${RunningX64}
		SetRegView 64
	${EndIf}
	${un.EnvVarUpdate} $0 "PATH" "R" "HKLM" "$InstallPath"	
	ExecWait "$UninstallString"
SectionEnd


Section "-Uninstall"
    Delete "$INSTDIR\Uninstall.exe"
    RMDir /r /REBOOTOK "$INSTDIR"    
    !insertmacro MUI_STARTMENU_GETFOLDER Application $StartMenuFolder
    Delete "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk"
    RMDir "$SMPROGRAMS\$StartMenuFolder"    
    DeleteRegKey /ifempty HKCU "${REGKEY}"
	DeleteRegKey HKCU "${UNINSTALL_REGKEY}"
SectionEnd


Function .onInit
    ${IfNot} ${RunningX64}
        MessageBox MB_ICONSTOP "This $(^Name) installer is suitable for 64-bit Windows only!"
        Abort
  ${EndIf}
FunctionEnd


Function un.onInit
    MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Are you sure you want to completely remove $(^Name) and all of its components?" IDYES +2
    Abort
FunctionEnd


Function un.onUninstSuccess
    HideWindow
    MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) was successfully removed from your computer."
FunctionEnd

