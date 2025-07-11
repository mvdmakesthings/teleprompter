@echo off
REM Build script for CueBird on Windows
REM Creates an executable and installer package

setlocal enabledelayedexpansion

echo.
echo ====================================
echo Building CueBird for Windows...
echo ====================================
echo.

REM Configuration
set APP_NAME=CueBird
set VERSION=0.1.0
set BUILD_DIR=dist

REM Clean previous builds
echo [BUILD] Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Check if we're in a virtual environment
if "%VIRTUAL_ENV%"=="" (
    echo [WARNING] Not in a virtual environment. Activating Poetry environment...
    call poetry shell
)

REM Install dependencies
echo [BUILD] Installing dependencies...
call poetry install

REM Create version info file for Windows
echo [BUILD] Creating version info file...
(
echo # UTF-8
echo #
echo # For more details about fixed file info 'ffi' see:
echo # http://msdn.microsoft.com/en-us/library/ms646997.aspx
echo VSVersionInfo^(
echo   ffi=FixedFileInfo^(
echo     # filevers and prodvers should be always a tuple with four items: ^(1, 2, 3, 4^)
echo     # Set not needed items to zero 0.
echo     filevers=^(0, 1, 0, 0^),
echo     prodvers=^(0, 1, 0, 0^),
echo     # Contains a bitmask that specifies the valid bits 'flags'r
echo     mask=0x3f,
echo     # Contains a bitmask that specifies the Boolean attributes of the file.
echo     flags=0x0,
echo     # The operating system for which this file was designed.
echo     # 0x4 - NT and there is no need to change it.
echo     OS=0x4,
echo     # The general type of file.
echo     # 0x1 - the file is an application.
echo     fileType=0x1,
echo     # The function of the file.
echo     # 0x0 - the function is not defined for this fileType
echo     subtype=0x0,
echo     # Creation date and time stamp.
echo     date=^(0, 0^)
echo   ^),
echo   kids=[
echo     StringFileInfo^(
echo       [
echo       StringTable^(
echo         u'040904B0',
echo         [StringStruct^(u'CompanyName', u'CueBird'^),
echo         StringStruct^(u'FileDescription', u'Professional Teleprompter Application'^),
echo         StringStruct^(u'FileVersion', u'0.1.0.0'^),
echo         StringStruct^(u'InternalName', u'CueBird'^),
echo         StringStruct^(u'LegalCopyright', u'Copyright © 2025 CueBird'^),
echo         StringStruct^(u'OriginalFilename', u'CueBird.exe'^),
echo         StringStruct^(u'ProductName', u'CueBird Teleprompter'^),
echo         StringStruct^(u'ProductVersion', u'0.1.0.0'^)]
echo       ^)
echo       ]
echo     ^),
echo     VarFileInfo^([VarStruct^(u'Translation', [1033, 1200]^)]^)
echo   ]
echo ^)
) > version_info.txt

REM Build the application
echo [BUILD] Building application with PyInstaller...
call poetry run pyinstaller cuebird.spec --clean --noconfirm

REM Check if build was successful
if not exist "dist\%APP_NAME%.exe" (
    echo [ERROR] Build failed! %APP_NAME%.exe not found in dist\
    exit /b 1
)

echo [BUILD] Build successful! %APP_NAME%.exe created.

REM Create installer script for Inno Setup
echo [BUILD] Creating Inno Setup script...
(
echo ; Inno Setup Script for CueBird
echo.
echo #define MyAppName "CueBird"
echo #define MyAppVersion "0.1.0"
echo #define MyAppPublisher "CueBird"
echo #define MyAppURL "https://github.com/mvdmakesthings/teleprompter"
echo #define MyAppExeName "CueBird.exe"
echo.
echo [Setup]
echo AppId={{E8F5C6D3-9A2B-4F1E-B7C8-D4A9E2F3B5C1}
echo AppName={#MyAppName}
echo AppVersion={#MyAppVersion}
echo AppPublisher={#MyAppPublisher}
echo AppPublisherURL={#MyAppURL}
echo AppSupportURL={#MyAppURL}
echo AppUpdatesURL={#MyAppURL}
echo DefaultDirName={autopf}\{#MyAppName}
echo DisableProgramGroupPage=yes
echo LicenseFile=LICENSE
echo OutputDir=dist
echo OutputBaseFilename=CueBird-{#MyAppVersion}-Windows-Setup
echo Compression=lzma
echo SolidCompression=yes
echo WizardStyle=modern
echo PrivilegesRequired=admin
echo.
echo [Languages]
echo Name: "english"; MessagesFile: "compiler:Default.isl"
echo.
echo [Tasks]
echo Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
echo.
echo [Files]
echo Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
echo Source: "dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
echo.
echo [Icons]
echo Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
echo Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
echo.
echo [Run]
echo Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange^(MyAppName, '&', '&&'^)}}"; Flags: nowait postinstall skipifsilent
echo.
echo [UninstallDelete]
echo Type: filesandordirs; Name: "{app}"
) > cuebird_installer.iss

REM Create a simple ZIP package as alternative
echo [BUILD] Creating ZIP package...
if exist "dist\CueBird-%VERSION%-Windows.zip" del "dist\CueBird-%VERSION%-Windows.zip"
cd dist
powershell -command "Compress-Archive -Path '%APP_NAME%.exe' -DestinationPath 'CueBird-%VERSION%-Windows.zip'"
cd ..

REM Create install instructions
echo [BUILD] Creating installation instructions...
(
echo CueBird Installation Instructions for Windows
echo ============================================
echo.
echo Option 1: Using the Installer ^(Recommended^)
echo -------------------------------------------
echo 1. Run CueBird-%VERSION%-Windows-Setup.exe
echo 2. Follow the installation wizard
echo 3. Launch CueBird from the Start Menu or Desktop
echo.
echo Option 2: Using the ZIP file
echo ---------------------------
echo 1. Extract CueBird-%VERSION%-Windows.zip to a folder
echo 2. Run CueBird.exe from the extracted folder
echo 3. ^(Optional^) Create a shortcut on your desktop
echo.
echo First Launch:
echo - Windows Defender may show a security warning
echo - Click "More info" then "Run anyway"
echo - Grant microphone access when prompted
echo.
echo System Requirements:
echo - Windows 10 or later ^(64-bit^)
echo - 4GB RAM recommended
echo - DirectX 9 or later
echo.
echo Troubleshooting:
echo - If the app doesn't start, install Visual C++ Redistributable
echo - For microphone issues, check Windows Settings ^> Privacy ^> Microphone
echo - Run as administrator if you encounter permission issues
echo.
echo Enjoy using CueBird!
) > "dist\INSTALL_INSTRUCTIONS.txt"

REM Clean up temporary files
del version_info.txt

echo.
echo ====================================
echo Build complete!
echo ====================================
echo.
echo Application: dist\%APP_NAME%.exe
echo ZIP Package: dist\CueBird-%VERSION%-Windows.zip
echo Installer Script: cuebird_installer.iss
echo Instructions: dist\INSTALL_INSTRUCTIONS.txt
echo.
echo Next steps:
echo 1. Test the application: dist\%APP_NAME%.exe
echo 2. ^(Optional^) Build installer with Inno Setup
echo 3. Distribute the ZIP or installer to users
echo.

REM Open the dist folder
explorer dist

pause