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
REM Stop Django server
REM ========================================
echo [1/4] Stopping Django server...
taskkill /F /FI "COMMANDLINE eq *manage.py runserver*" /FI "IMAGENAME eq python.exe" >NUL 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   [OK] Django server stopped
    set "STOPPED_ANYTHING=1"
) else (
    echo   [--] No Django server found
)

REM ========================================
REM Stop heartbeat updater
REM ========================================
echo [2/4] Stopping heartbeat updater...
taskkill /F /FI "WINDOWTITLE eq Heartbeat Updater*" >NUL 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   [OK] Heartbeat updater stopped
    set "STOPPED_ANYTHING=1"
) else (
    echo   [--] No heartbeat updater found
)

REM ========================================
REM Stop idle monitor
REM ========================================
echo [3/4] Stopping idle monitor...
taskkill /F /FI "COMMANDLINE eq *idle_monitor.py*" /FI "IMAGENAME eq python.exe" >NUL 2>&1
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
