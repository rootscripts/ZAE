@echo off
echo [ZAE] Installing ZaeTerminal on Windows...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Error: Python is not installed or not added to PATH.
    pause
    exit /b 1
)

python -c "import PyQt6" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ZAE] Installing PyQt6 dependency...
    python -m pip install PyQt6
)

set "TARGET_DIR=%USERPROFILE%\.local\bin"
set "CONFIG_DIR=%USERPROFILE%\.config\arch-greet\fonts"
set "APPS_DIR=%USERPROFILE%\AppData\Local\Microsoft\WindowsApps"

if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"
if not exist "%CONFIG_DIR%" mkdir "%CONFIG_DIR%"

if exist "%~dp0zae.py" (
    copy /Y "%~dp0zae.py" "%TARGET_DIR%\zae.py" >nul
) else (
    echo [ZAE] Downloading zae.py...
    python -c "import urllib.request, os, ssl; ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE; urllib.request.urlretrieve('https://raw.githubusercontent.com/rootscripts/ZAE/main/zae.py', os.path.expanduser('~/.local/bin/zae.py'), context=ctx)"
)

(
echo @echo off
echo python "%%USERPROFILE%%\.local\bin\zae.py" %%*
) > "%APPS_DIR%\zae.bat"

echo [ZAE] Installation finished! Open CMD or PowerShell and type 'zae' to start.
