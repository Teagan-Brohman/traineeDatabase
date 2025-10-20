@echo off
REM ========================================
REM Trainee Tracker - Stop Server
REM ========================================
REM This script forcefully stops the Django server
REM Use this if the server window is stuck or unresponsive
REM ========================================

echo.
echo ===============================================
echo    TRAINEE BADGE TRACKER - Stop Server
echo ===============================================
echo.

echo Looking for running Django processes...
echo.

REM Find and kill Python processes running manage.py
tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I /N "python.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo Found Python processes. Checking for Django server...

    REM Kill processes with manage.py in command line
    for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO LIST ^| find "PID:"') do (
        wmic process where "ProcessId=%%a" get CommandLine 2>NUL | find "manage.py runserver" >NUL
        if not errorlevel 1 (
            echo Stopping Django server (PID: %%a)...
            taskkill /PID %%a /F >NUL 2>&1
            echo Server stopped successfully!
        )
    )
) else (
    echo No Python processes found.
    echo The server may already be stopped.
)

REM ========================================
REM TEMPORARY: Cleanup server lock and background processes
REM ========================================
echo.
echo Cleaning up background processes...

REM Stop heartbeat updater (PowerShell process)
taskkill /FI "WINDOWTITLE eq Heartbeat Updater*" /F >NUL 2>&1
if %ERRORLEVEL% EQU 0 (
    echo - Heartbeat updater stopped
)

REM Stop idle monitor (Python process)
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO LIST ^| find "PID:"') do (
    wmic process where "ProcessId=%%a" get CommandLine 2>NUL | find "idle_monitor.py" >NUL
    if not errorlevel 1 (
        echo - Idle monitor stopped
        taskkill /PID %%a /F >NUL 2>&1
    )
)

REM Remove server lock file
if exist "SERVER_LOCK" (
    del SERVER_LOCK
    echo - Server lock file removed
)

REM Remove activity tracking file
if exist "LAST_ACTIVITY.txt" (
    del LAST_ACTIVITY.txt
    echo - Activity tracking file removed
)

echo Cleanup complete.

echo.
echo ===============================================
echo.
echo If the server is still running:
echo 1. Find the START_SERVER.bat window
echo 2. Press Ctrl+C
echo 3. Or just close the window
echo.
echo ===============================================
echo.
pause
