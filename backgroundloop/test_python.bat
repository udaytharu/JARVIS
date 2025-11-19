@echo off
setlocal enabledelayedexpansion

echo ========================================
echo JARVIS AI - Python Script Test
echo ========================================
echo.

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
set "PYTHON_SCRIPT=%SCRIPT_DIR%listen.py"

echo Current directory: %SCRIPT_DIR%
echo Python script: %PYTHON_SCRIPT%
echo Project root: %PROJECT_ROOT%
echo.

if not exist "%PYTHON_SCRIPT%" (
    echo ERROR: listen.py not found!
    pause
    exit /b 1
)

echo Checking Python installations...

rem Check for Python installations
set "PYTHON_FOUND="
set "PYTHON_PATH="

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

echo Testing Python script execution...
echo Command: !PYTHON_PATH! "%PYTHON_SCRIPT%" --phrase "launch jarvis" --bat "%PROJECT_ROOT%\JARVIS_START.bat"
echo.
echo The script will start listening for "launch jarvis"...
echo Press Ctrl+C to stop the test.
echo.

rem Test the Python script
!PYTHON_PATH! "%PYTHON_SCRIPT%" --phrase "launch jarvis" --bat "%PROJECT_ROOT%\JARVIS_START.bat"

echo.
echo Test completed.
pause
exit /b 0

endlocal
