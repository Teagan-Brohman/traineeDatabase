@echo off
setlocal enabledelayedexpansion
REM ========================================
REM Trainee Tracker - Start Server
REM ========================================
REM This script starts the Django web server
REM Double-click this file to start the application
REM ========================================

echo.
echo ===============================================
echo    TRAINEE BADGE TRACKER - Starting Server
echo ===============================================
echo.

REM Check for bundled WinPython (highest priority)
set "PYTHON_CMD=python"
set "WINPYTHON_DETECTED=0"

if exist "portable_python\" (
    REM Check if WinPython is already extracted
    if exist "portable_python\WPy64-312101\python\python.exe" (
        set "PYTHON_CMD=portable_python\WPy64-312101\python\python.exe"
        set "WINPYTHON_DETECTED=1"
        echo [INFO] Using portable WinPython 3.12.10
    )
)

REM Check for custom Python path configuration (if WinPython not found)
if "%WINPYTHON_DETECTED%"=="0" (
    if exist "PYTHON_PATH.txt" (
        echo [INFO] Checking for custom Python path...
        for /f "usebackq tokens=2* delims==" %%a in (`findstr /v "^REM" PYTHON_PATH.txt ^| findstr "PYTHON_PATH"`) do (
            set "PYTHON_CMD=%%a"
        )
        if not "%PYTHON_CMD%"=="python" (
            echo [INFO] Using custom Python from PYTHON_PATH.txt
        )
    )
)

REM Check if Python is available
"%PYTHON_CMD%" --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not found at: %PYTHON_CMD%
    echo.
    echo Please run FIRST_TIME_SETUP.bat first or install Python
    echo.
    pause
    exit /b 1
)

echo [1/6] Checking Python version...
"%PYTHON_CMD%" --version

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo.
    echo ERROR: Virtual environment not found!
    echo Please run FIRST_TIME_SETUP.bat first
    echo.
    pause
    exit /b 1
)

echo [2/6] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/6] Checking for server lock...
REM ========================================
REM TEMPORARY: Hybrid lock detection system
REM This prevents multiple servers from running
REM simultaneously on SQLite network drive.
REM REMOVE when migrating to PostgreSQL.
REM ========================================

if exist "SERVER_LOCK" (
    REM Read lock file information
    for /f "tokens=2*" %%a in ('findstr "COMPUTER:" SERVER_LOCK') do set LOCK_COMPUTER=%%b
    for /f "tokens=2*" %%a in ('findstr "STARTED:" SERVER_LOCK') do set LOCK_STARTED=%%b
    for /f "tokens=2*" %%a in ('findstr "LAST_HEARTBEAT:" SERVER_LOCK') do set LOCK_HEARTBEAT=%%b

    REM Calculate lock age in minutes using PowerShell
    for /f %%i in ('powershell -Command "if (Test-Path 'SERVER_LOCK') { $lockTime = (Get-Item 'SERVER_LOCK').LastWriteTime; $age = (Get-Date) - $lockTime; [int]$age.TotalMinutes } else { 0 }"') do set LOCK_AGE_MINUTES=%%i

    REM Apply hybrid lock logic
    if !LOCK_AGE_MINUTES! GTR 10 (
        REM Lock is over 10 minutes old - definitely stale, auto-clean
        echo.
        echo ===============================================
        echo AUTO-RECOVERY: Stale lock detected
        echo ===============================================
        echo Lock age: !LOCK_AGE_MINUTES! minutes
        echo Previous server: !LOCK_COMPUTER!
        echo Started: !LOCK_STARTED!
        echo.
        echo This lock is stale - over 10 minutes old.
        echo The previous server likely crashed.
        echo Auto-cleaning and starting new server...
        echo ===============================================
        del SERVER_LOCK
        timeout /t 2 /nobreak >nul
        goto :lock_check_done
    )

    if !LOCK_AGE_MINUTES! GTR 5 (
        REM Lock is 5-10 minutes old - might be stale, ask user
        echo.
        echo ===============================================
        echo WARNING: Server lock detected
        echo ===============================================
        echo Lock age: !LOCK_AGE_MINUTES! minutes
        echo Computer: !LOCK_COMPUTER!
        echo Started: !LOCK_STARTED!
        echo Last heartbeat: !LOCK_HEARTBEAT!
        echo.
        echo This lock might be stale. The server may have crashed.
        echo.
        echo Options:
        echo   [F] Force unlock and start server
        echo   [X] Exit and investigate
        echo.
        choice /c FX /n /m "Your choice: "
        if errorlevel 2 exit /b 1
        if errorlevel 1 del SERVER_LOCK
        timeout /t 1 /nobreak >nul
        goto :lock_check_done
    )

    REM Lock is less than 5 minutes old - definitely active, hard block
    echo.
    echo ===============================================
    echo ERROR: Server already running!
    echo ===============================================
    echo Computer: !LOCK_COMPUTER!
    echo Started: !LOCK_STARTED!
    echo Last heartbeat: !LOCK_HEARTBEAT!
    echo Lock age: !LOCK_AGE_MINUTES! minutes
    echo.
    echo A server is actively running. Please:
    echo   1. Use the existing server, OR
    echo   2. Stop it using STOP_SERVER.bat on !LOCK_COMPUTER!
    echo.
    echo ===============================================
    pause
    exit /b 1
)

:lock_check_done

REM Check if port 8000 is in use (additional safety check)
netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    echo.
    echo WARNING: Port 8000 is in use on this computer!
    echo Please close any other servers before continuing.
    echo.
    pause
    exit /b 1
)

echo [4/6] Running database migrations...
python manage.py migrate --noinput

echo [5/6] Checking for admin user...
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trainee_tracker.settings'); import django; django.setup(); from django.contrib.auth.models import User; print('Admin exists' if User.objects.filter(is_superuser=True).exists() else 'No admin found')"

echo [6/6] Starting server...

REM ========================================
REM Create server lock file
REM ========================================
echo COMPUTER: %COMPUTERNAME% > SERVER_LOCK
echo USER: %USERNAME% >> SERVER_LOCK
echo STARTED: %DATE% %TIME% >> SERVER_LOCK
echo LAST_HEARTBEAT: %DATE% %TIME% >> SERVER_LOCK
echo PID: %RANDOM%%RANDOM% >> SERVER_LOCK

REM Get and save IP address
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set IP=%%a
    set IP=!IP:~1!
    echo IP: !IP! >> SERVER_LOCK
)

echo Lock file created successfully.

REM ========================================
REM Start heartbeat updater (background)
REM ========================================
echo Starting heartbeat updater...
start /min "Heartbeat Updater" powershell -ExecutionPolicy Bypass -WindowStyle Hidden -File "%CD%\heartbeat_updater.ps1"
timeout /t 2 /nobreak >nul

REM ========================================
REM Start idle monitor (background)
REM ========================================
echo Starting idle monitor (timeout: 20 minutes)...
start /min "Idle Monitor" python "%CD%\idle_monitor.py"
timeout /t 2 /nobreak >nul

echo.
echo ===============================================
echo    SERVER IS STARTING
echo ===============================================
echo.
echo The server will be accessible at:
echo.
echo   - On this computer: http://localhost:8000
echo   - On the network:   http://%COMPUTERNAME%:8000
echo.
echo To find your IP address, check the output below.
echo Share this address with other users.
echo.
echo ===============================================
echo IMPORTANT: Keep this window open!
echo           Closing it will stop the server.
echo ===============================================
echo.
echo TEMPORARY SAFEGUARDS ACTIVE:
echo - Server lock prevents multiple instances
echo - Auto-shutdown after 20 min of inactivity
echo - Heartbeat updates every 60 seconds
echo ===============================================
echo.

REM Display IP address
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set IP=%%a
    set IP=!IP:~1!
    echo Your IP Address: !IP!:8000
)

echo.
echo Starting Django server...
echo.
python manage.py runserver 0.0.0.0:8000

REM ========================================
REM Cleanup on server stop
REM ========================================
echo.
echo ===============================================
echo Server has stopped.
echo ===============================================
echo Cleaning up lock file...
if exist "SERVER_LOCK" del SERVER_LOCK
echo Cleanup complete.
echo.
pause
