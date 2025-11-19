@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

set "LOGFILE=%~dp0listen.log"
set "ERROR_LOG=%~dp0error.log"
set "PROJECT_ROOT=%~dp0.."
set "PY_LAUNCHER=%SystemRoot%\py.exe"

:loop
if exist "%PROJECT_ROOT%\venv\Scripts\python.exe" (
    echo [%DATE% %TIME%] Using venv python >> "%LOGFILE%"
    "%PROJECT_ROOT%\venv\Scripts\python.exe" -u "%~dp0listen.py" >> "%LOGFILE%" 2>&1
) else if exist "%PROJECT_ROOT%\env\Scripts\python.exe" (
    echo [%DATE% %TIME%] Using env python >> "%LOGFILE%"
    "%PROJECT_ROOT%\env\Scripts\python.exe" -u "%~dp0listen.py" >> "%LOGFILE%" 2>&1
) else if exist "%PY_LAUNCHER%" (
    echo [%DATE% %TIME%] Using py launcher >> "%LOGFILE%"
    py -3 -u "%~dp0listen.py" >> "%LOGFILE%" 2>&1
) else (
    echo [%DATE% %TIME%] Using system PATH python >> "%LOGFILE%"
    python -u "%~dp0listen.py" >> "%LOGFILE%" 2>&1
)

set "EXIT_CODE=%ERRORLEVEL%"
if %EXIT_CODE% neq 0 (
    echo [%DATE% %TIME%] listen.py exited with code %EXIT_CODE% >> "%ERROR_LOG%"
)

timeout /t 10 /nobreak >nul
goto loop

endlocal

