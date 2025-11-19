@echo off
setlocal enabledelayedexpansion

echo ========================================
echo JARVIS AI - Direct Startup Installation
echo ========================================
echo.

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
set "PYTHON_SCRIPT=%SCRIPT_DIR%listen.py"

echo Checking required files...
if not exist "%PYTHON_SCRIPT%" (
    echo ERROR: listen.py not found at "%PYTHON_SCRIPT%"
    echo Current directory: %SCRIPT_DIR%
    pause
    exit /b 1
)

echo Files found successfully.
echo Python script: %PYTHON_SCRIPT%
echo Project root: %PROJECT_ROOT%
echo.

rem Check for Python installations
set "PYTHON_FOUND="
set "PYTHON_PATH="

echo Checking Python installations...

rem Check for virtual environment first
if exist "%PROJECT_ROOT%\venv\Scripts\python.exe" (
    set "PYTHON_PATH=%PROJECT_ROOT%\venv\Scripts\python.exe"
    set "PYTHON_FOUND=1"
    echo Found virtual environment Python: !PYTHON_PATH!
) else if exist "%PROJECT_ROOT%\env\Scripts\python.exe" (
    set "PYTHON_PATH=%PROJECT_ROOT%\env\Scripts\python.exe"
    set "PYTHON_FOUND=1"
    echo Found environment Python: !PYTHON_PATH!
) else (
    rem Check system Python
    python --version >nul 2>&1
    if !ERRORLEVEL!==0 (
        set "PYTHON_PATH=python"
        set "PYTHON_FOUND=1"
        echo Found system Python: !PYTHON_PATH!
    ) else (
        rem Check Python3
        python3 --version >nul 2>&1
        if !ERRORLEVEL!==0 (
            set "PYTHON_PATH=python3"
            set "PYTHON_FOUND=1"
            echo Found system Python3: !PYTHON_PATH!
        )
    )
)

if not defined PYTHON_FOUND (
    echo ERROR: No Python installation found!
    echo Please install Python or create a virtual environment.
    pause
    exit /b 1
)

echo.
echo Using Python: !PYTHON_PATH!
echo.

rem Clean up old startup tasks
echo Cleaning up old startup tasks...
schtasks /Delete /TN "JarvisBackgroundListener" /F >nul 2>&1
schtasks /Delete /TN "JarvisBackgroundListener-Logon" /F >nul 2>&1
schtasks /Delete /TN "JarvisBackgroundListener-Startup" /F >nul 2>&1
schtasks /Delete /TN "JarvisDirectStartup" /F >nul 2>&1

echo Creating new startup task...

rem Create a startup task that runs the Python script directly
schtasks /Create ^
  /SC ONLOGON ^
  /RL HIGHEST ^
  /TN "JarvisDirectStartup" ^
  /TR "!PYTHON_PATH! \"%PYTHON_SCRIPT%\" --phrase \"launch jarvis\" --bat \"%PROJECT_ROOT%\JARVIS_START.bat\"" ^
  /F

if not !ERRORLEVEL!==0 (
    echo Failed to create startup task. Error code: !ERRORLEVEL!
    echo Try running this script as Administrator.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Startup task created successfully!
echo ========================================
echo.
echo Task name: JarvisDirectStartup
echo Python: !PYTHON_PATH!
echo Script: %PYTHON_SCRIPT%
echo.
echo The script will now run automatically when you log in.
echo It will listen for "launch jarvis" and start JARVIS when heard.
echo.
echo To verify: schtasks /Query /TN "JarvisDirectStartup"
echo To remove: schtasks /Delete /TN "JarvisDirectStartup" /F
echo.
echo Testing the startup command...
echo Running: !PYTHON_PATH! "%PYTHON_SCRIPT%" --phrase "launch jarvis" --bat "%PROJECT_ROOT%\JARVIS_START.bat"

rem Test the command
!PYTHON_PATH! "%PYTHON_SCRIPT%" --phrase "launch jarvis" --bat "%PROJECT_ROOT%\JARVIS_START.bat"

echo.
echo Test completed. The script should now be running in the background.
echo Check Task Manager to see if listen.py is running.
echo.
pause
exit /b 0

endlocal
