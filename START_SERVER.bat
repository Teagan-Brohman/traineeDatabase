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

echo [3/6] Checking if server is already running...
netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo.
    echo ===============================================
    echo WARNING: Server already running on port 8000!
    echo ===============================================
    echo.
    echo A Django server is already running.
    echo.
    echo Options:
    echo   1. Use the existing server (close this window)
    echo   2. Stop it first using STOP_SERVER.bat
    echo   3. Close the other START_SERVER.bat window
    echo.
    echo ===============================================
    pause
    exit /b 1
)

echo [4/6] Running database migrations...
python manage.py migrate --noinput

echo [5/6] Checking for admin user...
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trainee_tracker.settings'); import django; django.setup(); from django.contrib.auth.models import User; print('Admin exists' if User.objects.filter(is_superuser=True).exists() else 'No admin found')"

echo [6/6] Starting server...
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

REM Get and display IP address
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set IP=%%a
    set IP=!IP:~1!
    echo Your IP Address: !IP!:8000
)

echo.
echo Starting Django server...
echo.
python manage.py runserver 0.0.0.0:8000

REM If server stops, show message
echo.
echo ===============================================
echo Server has stopped.
echo ===============================================
pause
