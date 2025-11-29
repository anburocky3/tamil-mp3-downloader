@echo off
REM Release build_exe.bat - parenthesis-safe minimal version
REM Usage: build_exe.bat [--icon path\to\icon.ico]

setlocal
set SPEC_FILE=tamil_mp3_downloader.spec
set ICON_PATH=
set VERSION=0.0.0
set NAME=tamil-mp3-downloader

:parse_args
if "%~1"=="--icon" set ICON_PATH=--icon "%~2" & shift & shift & goto parse_args

echo Checking for PyInstaller and installing/upgrading if needed...
call python -m pip install --upgrade pip >nul 2>&1
call python -m pip install --upgrade pyinstaller >nul 2>&1
set RC=%ERRORLEVEL%
if not "%RC%"=="0" echo Failed to install pyinstaller; please run: python -m pip install pyinstaller & exit /b 1

echo Installing runtime requirements from requirements.txt (so they are bundled into the EXE)...
if exist requirements.txt (
  call python -m pip install -r requirements.txt >nul 2>&1
  set RC=%ERRORLEVEL%
  if not "%RC%"=="0" echo Failed to install some requirements; continuing anyway.
) else (
  echo No requirements.txt found, skipping installing runtime dependencies.
)

:: read VERSION file if present (used to name the EXE)
if exist VERSION (
  for /f "usebackq delims=" %%V in ("VERSION") do set VERSION=%%V
)
if not "%VERSION%"=="0.0.0" set NAME=tamil-mp3-downloader-v%VERSION%

echo Running PyInstaller (this may take several minutes)...
if exist "%SPEC_FILE%" (
  call pyinstaller --clean --noconfirm %ICON_PATH% "%SPEC_FILE%"
) else (
  call pyinstaller --clean --noconfirm --onefile --console --name "%NAME%" %ICON_PATH% --add-data "data;data" --add-data "data\old;data\old" --add-data "screenshots;screenshots" main.py
)

echo.
echo Build finished.
echo The single-file EXE will be located at: dist\%NAME%.exe
echo If you want an icon, re-run this script with: build_exe.bat --icon path\to\icon.ico
echo Note: Some antivirus engines may flag freshly-built EXEs as suspicious.
echo Done.
