@echo off
echo ========================================
echo JARVIS AI - Direct Startup Uninstall
echo ========================================
echo.

echo Removing startup task...

rem Remove the direct startup task
schtasks /Delete /TN "JarvisDirectStartup" /F >nul 2>&1
if %ERRORLEVEL%==0 (
    echo Removed: JarvisDirectStartup
) else (
    echo Task JarvisDirectStartup not found or already removed
)

rem Also remove any old legacy tasks
schtasks /Delete /TN "JarvisBackgroundListener" /F >nul 2>&1
schtasks /Delete /TN "JarvisBackgroundListener-Logon" /F >nul 2>&1
schtasks /Delete /TN "JarvisBackgroundListener-Startup" /F >nul 2>&1

echo.
echo ========================================
echo Startup task removed successfully!
echo ========================================
echo.
echo To verify no tasks remain, run: schtasks /Query /TN "Jarvis*"
echo.
pause
exit /b 0
