@echo off
setlocal EnableDelayedExpansion

set "RAW=https://raw.githubusercontent.com/rootscripts/ZAE/main/zae.py"
set "DEST=%USERPROFILE%\.zae"

if not exist "%DEST%" mkdir "%DEST%"

echo [zae] downloading zae.py ...
curl -fsSL "%RAW%" -o "%DEST%\zae.py"
if errorlevel 1 (
    echo [zae] download failed. check your connection.
    pause
    exit /b 1
)

set "PY="
where python >nul 2>&1 && for /f "delims=" %%i in ('where python') do if not defined PY set "PY=%%i"
if not defined PY where py >nul 2>&1 && for /f "delims=" %%i in ('where py') do if not defined PY set "PY=%%i"
if not defined PY (
    for %%d in (
        "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
        "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
        "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
        "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
        "%PROGRAMFILES%\Python313\python.exe"
        "%PROGRAMFILES%\Python312\python.exe"
        "%PROGRAMFILES%\Python311\python.exe"
        "%PROGRAMFILES%\Python310\python.exe"
    ) do (
        if exist %%d if not defined PY set "PY=%%~d"
    )
)

if not defined PY (
    echo [zae] python not found. install python from python.org
    pause
    exit /b 1
)

echo [zae] python found: %PY%

(
    echo @echo off
    echo start "" "%PY%" "%DEST%\zae.py" %%*
) > "%DEST%\zae.bat"

set "INPATH=0"
echo %PATH% | findstr /i /c:"%DEST%" >nul 2>&1 && set "INPATH=1"

if "!INPATH!"=="0" (
    echo [zae] adding %DEST% to PATH ...
    setx PATH "%DEST%;%PATH%" >nul 2>&1
    set "PATH=%DEST%;%PATH%"
)

echo [zae] installed. open a new cmd and type: zae
echo [zae] if 'zae' is not recognized, reopen your terminal.
pause
