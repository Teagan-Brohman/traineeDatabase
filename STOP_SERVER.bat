@echo off
setlocal enabledelayedexpansion
REM ========================================
REM Trainee Tracker - Stop Server
REM ========================================
REM This script gracefully stops the Django server
REM and all background processes (heartbeat, idle monitor)
REM without affecting the START_SERVER.bat window.
REM ========================================

echo.
echo ===============================================
echo    TRAINEE BADGE TRACKER - Stop Server
echo ===============================================
echo.

set "STOPPED_ANYTHING=0"

REM ========================================
REM Stop Django server (by port 8000)
REM ========================================
echo [1/4] Stopping Django server...

REM Find PID of process listening on port 8000
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
    set "DJANGO_PID=%%a"
    goto :found_django
)
set "DJANGO_PID="

:found_django
if defined DJANGO_PID (
    taskkill /PID !DJANGO_PID! /F >NUL 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo   [OK] Django server stopped ^(PID: !DJANGO_PID!^)
        set "STOPPED_ANYTHING=1"
    ) else (
        echo   [!!] Failed to stop Django server ^(PID: !DJANGO_PID!^)
    )
) else (
    echo   [--] No Django server found ^(port 8000 not in use^)
)

REM ========================================
REM Stop heartbeat updater
REM ========================================
echo [2/4] Stopping heartbeat updater...

REM First check if process exists
tasklist /FI "WINDOWTITLE eq Heartbeat Updater*" 2>NUL | find /I "powershell.exe" >NUL
if %ERRORLEVEL% EQU 0 (
    REM Process exists, kill it
    taskkill /F /FI "WINDOWTITLE eq Heartbeat Updater*" >NUL 2>&1
    echo   [OK] Heartbeat updater stopped
    set "STOPPED_ANYTHING=1"
) else (
    echo   [--] No heartbeat updater found
)

REM ========================================
REM Stop idle monitor (using PowerShell with WMI)
REM ========================================
echo [3/4] Stopping idle monitor...

REM Use PowerShell with WMI to find and kill idle_monitor.py process
REM Avoid complex Filter escaping by using Where-Object for all filtering
powershell -Command "$found = $false; Get-WmiObject Win32_Process | Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -like '*idle_monitor.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue; $found = $true }; if ($found) { exit 0 } else { exit 1 }" >NUL 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   [OK] Idle monitor stopped
    set "STOPPED_ANYTHING=1"
) else (
    echo   [--] No idle monitor found
)

REM ========================================
REM Clean up lock and tracking files
REM ========================================
echo [4/4] Cleaning up lock files...

set "CLEANED_FILES=0"

if exist "SERVER_LOCK" (
    del "SERVER_LOCK"
    echo   [OK] Server lock file removed
    set "CLEANED_FILES=1"
)

if exist "LAST_ACTIVITY.txt" (
    del "LAST_ACTIVITY.txt"
    echo   [OK] Activity tracking file removed
    set "CLEANED_FILES=1"
)

if "%CLEANED_FILES%"=="0" (
    echo   [--] No lock files found
)

echo.
echo ===============================================

if "%STOPPED_ANYTHING%"=="1" (
    echo SUCCESS: Server and background processes stopped
    echo.
    echo The START_SERVER.bat window should show:
    echo   "Server has stopped. Cleaning up lock file..."
    echo.
    echo To restart, run START_SERVER.bat again.
) else (
    echo NOTICE: No running server found
    echo.
    echo The server may already be stopped, or was not
    echo started using START_SERVER.bat.
)

echo ===============================================
echo.
pause
