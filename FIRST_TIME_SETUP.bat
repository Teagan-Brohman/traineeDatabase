@echo off
setlocal enabledelayedexpansion
REM ========================================
REM Trainee Tracker - First Time Setup
REM ========================================
REM Run this ONCE before using the application
REM This sets up the database and creates an admin user
REM ========================================

echo.
echo ===============================================
echo    TRAINEE BADGE TRACKER - First Time Setup
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
    echo Options to fix this:
    echo.
    echo 1. Install Python 3.8+ from python.org
    echo    During installation, check "Add Python to PATH"
    echo.
    echo 2. If you have portable Python, edit PYTHON_PATH.txt
    echo    Remove "REM" and set the full path to python.exe
    echo    Example: SET PYTHON_PATH=C:\PortablePython\python.exe
    echo.
    pause
    exit /b 1
)

echo [STEP 1/6] Python found!
"%PYTHON_CMD%" --version
echo.

REM Check if virtual environment exists and is valid
echo [STEP 2/6] Checking virtual environment...
if exist "venv\Scripts\python.exe" (
    echo Virtual environment found, testing compatibility...
    venv\Scripts\python.exe --version >nul 2>&1
    if errorlevel 1 (
        echo Virtual environment appears corrupted, recreating...
        rmdir /s /q venv
        goto CREATE_VENV
    ) else (
        echo Virtual environment is valid!
        goto SKIP_VENV
    )
) else (
    :CREATE_VENV
    echo Creating virtual environment...
    "%PYTHON_CMD%" -m venv venv
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to create virtual environment
        echo Make sure you have venv module installed
        echo.
        pause
        exit /b 1
    )
    echo Virtual environment created successfully!
)

:SKIP_VENV
echo.

echo [STEP 3/6] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

echo [STEP 4/6] Installing required packages...
echo This may take a few minutes...
"%PYTHON_CMD%" -m pip install --upgrade pip --quiet
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install packages
    echo Check your internet connection and try again
    echo.
    pause
    exit /b 1
)
echo Packages installed successfully!
echo.

echo [STEP 5/6] Setting up database...
python manage.py migrate
if errorlevel 1 (
    echo.
    echo ERROR: Database migration failed
    echo.
    pause
    exit /b 1
)
echo Database set up successfully!
echo.

echo [STEP 6/6] Creating admin user...
echo.
echo You will be prompted to create an administrator account.
echo This account will be used to:
echo   - Access the admin panel at /admin/
echo   - Create staff accounts
echo   - Manage trainees and tasks
echo.
echo IMPORTANT: Remember the username and password you create!
echo.
pause

python manage.py createsuperuser
if errorlevel 1 (
    echo.
    echo Note: If admin user already exists, that's okay!
    echo.
)

echo.
echo ===============================================
echo    SETUP COMPLETE!
echo ===============================================
echo.
echo What's next:
echo.
echo 1. Import your trainee data (optional):
echo    - Run: python import_data.py
echo.
echo 2. Start the server:
echo    - Double-click START_SERVER.bat
echo.
echo 3. Access the application:
echo    - Open browser: http://localhost:8000
echo.
echo 4. Create staff accounts:
echo    - Go to: http://localhost:8000/admin/
echo    - Login with the admin account you just created
echo    - Add staff users
echo.
echo ===============================================
echo.
pause
