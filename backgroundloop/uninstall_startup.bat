@echo off
setlocal

echo Uninstalling JARVIS AI startup tasks...
echo.

echo Removing startup tasks...

rem Remove all JARVIS startup tasks
schtasks /Delete /TN "JarvisBackgroundListener" /F >nul 2>&1
if %ERRORLEVEL%==0 (
    echo Removed: JarvisBackgroundListener
) else (
    echo Task JarvisBackgroundListener not found or already removed
)

schtasks /Delete /TN "JarvisBackgroundListener-Logon" /F >nul 2>&1
if %ERRORLEVEL%==0 (
    echo Removed: JarvisBackgroundListener-Logon
) else (
    echo Task JarvisBackgroundListener-Logon not found or already removed
)

schtasks /Delete /TN "JarvisBackgroundListener-Startup" /F >nul 2>&1
if %ERRORLEVEL%==0 (
    echo Removed: JarvisBackgroundListener-Startup
) else (
    echo Task JarvisBackgroundListener-Startup not found or already removed
)

echo.
echo ========================================
echo Startup tasks removed successfully!
echo ========================================
echo.
echo To verify no tasks remain, run: schtasks /Query /TN "JarvisBackgroundListener*"
echo.
pause
exit /b 0

endlocal


