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

REM Check for custom Python path configuration
if exist "PYTHON_PATH.txt" (
    echo [INFO] Checking for custom Python path...
    for /f "tokens=2 delims==" %%a in ('findstr /v "^REM" PYTHON_PATH.txt ^| findstr "PYTHON_PATH"') do (
        set "PYTHON_CMD=%%a"
        set "PYTHON_CMD=!PYTHON_CMD: =!"
    )

    if defined PYTHON_CMD (
        echo [INFO] Using custom Python: !PYTHON_CMD!
    ) else (
        set "PYTHON_CMD=python"
    )
) else (
    set "PYTHON_CMD=python"
)

REM Check if Python is available
"%PYTHON_CMD%" --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not found at: %PYTHON_CMD%
    echo.
    echo Please install Python 3.8+ or edit PYTHON_PATH.txt
    echo with your portable Python installation path
    echo.
    pause
    exit /b 1
)

echo [1/5] Checking Python version...
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

echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/5] Running database migrations...
python manage.py migrate --noinput

echo [4/5] Checking for admin user...
python -c "import django; django.setup(); from django.contrib.auth.models import User; print('Admin exists' if User.objects.filter(is_superuser=True).exists() else 'No admin found')"

echo [5/5] Starting server...
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
