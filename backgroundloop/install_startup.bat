@echo off
setlocal

echo Installing JARVIS AI startup tasks...
echo.

set "SCRIPT_DIR=%~dp0"
set "VBS=%SCRIPT_DIR%run_hidden.vbs"
set "BAT=%SCRIPT_DIR%run_listen.bat"

echo Checking required files...
if not exist "%VBS%" (
  echo Error: run_hidden.vbs not found at "%VBS%"
  echo Current directory: %SCRIPT_DIR%
  pause
  exit /b 1
)

if not exist "%BAT%" (
  echo Error: run_listen.bat not found at "%BAT%"
  echo Current directory: %SCRIPT_DIR%
  pause
  exit /b 1
)

echo Files found successfully.
echo VBS: %VBS%
echo BAT: %BAT%
echo.

rem Get absolute paths
for /f "usebackq tokens=*" %%A in (`powershell -NoProfile -Command "(Resolve-Path '%VBS%').Path"`) do set "VBS_ABS=%%A"
for /f "usebackq tokens=*" %%A in (`powershell -NoProfile -Command "(Resolve-Path '%BAT%').Path"`) do set "BAT_ABS=%%A"

echo Using absolute paths:
echo VBS: %VBS_ABS%
echo BAT: %BAT_ABS%
echo.

rem Clean up legacy task names if present
echo Cleaning up old startup tasks...
schtasks /Delete /TN "JarvisBackgroundListener" /F >nul 2>&1
schtasks /Delete /TN "JarvisBackgroundListener-Logon" /F >nul 2>&1
schtasks /Delete /TN "JarvisBackgroundListener-Startup" /F >nul 2>&1

echo Creating startup tasks...

rem Task 1: Run at user logon (recommended for microphone access)
echo Creating logon task...
schtasks /Create ^
  /SC ONLOGON ^
  /RL HIGHEST ^
  /TN "JarvisBackgroundListener-Logon" ^
  /TR "wscript.exe \"%VBS_ABS%\"" ^
  /F
if not %ERRORLEVEL%==0 (
  echo Failed to create 'JarvisBackgroundListener-Logon'. Try running as Administrator.
  echo Error code: %ERRORLEVEL%
  pause
  exit /b 1
)

rem Task 2: Run at system startup (delayed, runs under SYSTEM)
echo Creating system startup task...
schtasks /Create ^
  /SC ONSTART ^
  /DELAY 0000:30 ^
  /RL HIGHEST ^
  /RU SYSTEM ^
  /TN "JarvisBackgroundListener-Startup" ^
  /TR "wscript.exe \"%VBS_ABS%\"" ^
  /F
if not %ERRORLEVEL%==0 (
  echo Failed to create 'JarvisBackgroundListener-Startup'. Try running as Administrator.
  echo Error code: %ERRORLEVEL%
  pause
  exit /b 1
)

echo.
echo ========================================
echo Startup tasks created successfully!
echo ========================================
echo.
echo Created tasks:
echo - JarvisBackgroundListener-Logon (runs at user logon)
echo - JarvisBackgroundListener-Startup (runs at system startup, delayed 30 seconds)
echo.
echo To verify, run: schtasks /Query /TN "JarvisBackgroundListener*"
echo To remove tasks: schtasks /Delete /TN "JarvisBackgroundListener*" /F
echo.
pause
exit /b 0

endlocal


