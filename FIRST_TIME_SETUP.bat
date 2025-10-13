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

REM Check for bundled WinPython (highest priority)
set "PYTHON_CMD=python"
set "WINPYTHON_DETECTED=0"

if exist "portable_python\" (
    echo [INFO] Checking for portable Python...

    REM Check if WinPython is already extracted
    if exist "portable_python\WPy64-312101\python\python.exe" (
        set "PYTHON_CMD=portable_python\WPy64-312101\python\python.exe"
        set "WINPYTHON_DETECTED=1"
        echo [INFO] Using portable WinPython 3.12.10
    ) else if exist "portable_python\Winpython64-3.12.10.1dot.exe" (
        echo [INFO] Extracting WinPython portable distribution...
        echo [INFO] This may take a minute...
        cd portable_python
        Winpython64-3.12.10.1dot.exe -y -o"." >nul 2>&1
        cd ..
        if exist "portable_python\WPy64-312101\python\python.exe" (
            set "PYTHON_CMD=portable_python\WPy64-312101\python\python.exe"
            set "WINPYTHON_DETECTED=1"
            echo [SUCCESS] WinPython extracted successfully
        ) else (
            echo [WARN] WinPython extraction failed - will try system Python
        )
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
"%PYTHON_CMD%" --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not found at: %PYTHON_CMD%
    echo.
    echo Options to fix this:
    echo.
    echo 1. Add WinPython to portable_python/ folder (see portable_python/README.txt)
    echo    Download: https://github.com/winpython/winpython/releases
    echo    File: Winpython64-3.12.10.1dot.exe (23 MB)
    echo.
    echo 2. Install Python 3.10-3.13 (64-bit) from python.org
    echo    During installation, check "Add Python to PATH"
    echo.
    echo 3. If you have portable Python, edit PYTHON_PATH.txt
    echo    Remove "REM" and set the full path to python.exe
    echo    Example: SET PYTHON_PATH=C:\PortablePython\python.exe
    echo.
    pause
    
)

echo [STEP 1/6] Python found!
"%PYTHON_CMD%" --version
echo.

REM Check if virtual environment exists and is valid
echo [STEP 2/6] Checking virtual environment...
if exist "venv\Scripts\python.exe" (
    echo Virtual environment found, testing compatibility...
    venv\Scripts\python.exe --version
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
"%PYTHON_CMD%" -m pip install --upgrade pip

REM Try offline installation first from bundled wheels
if exist "wheels\" (
    echo [INFO] Pre-built packages found - Attempting offline installation
    echo [INFO] This works without internet and requires no build tools
    echo.
    pip install --no-index --find-links=wheels -r requirements.txt
    if errorlevel 1 (
        echo.
        echo [WARN] Offline installation failed
        echo [INFO] Falling back to online installation from PyPI
        echo.
        pip install -r requirements.txt
        if errorlevel 1 (
            echo.
            echo ERROR: Failed to install packages from PyPI
            echo.
            echo Possible issues:
            echo   - No internet connection
            echo   - Python version not supported - need Python 3.10-3.13 64-bit
            echo   - Package build tools missing
            echo.
            echo Supported: Python 3.10, 3.11, 3.12, 3.13 - 64-bit Windows only
            echo Your version:
            python --version
            echo.
            pause
            exit /b 1
        )
        echo Packages installed successfully from PyPI
        echo.
    ) else (
        echo [SUCCESS] Offline installation completed - No internet required
        echo.
    )
) else (
    echo [INFO] No pre-built packages found - downloading from PyPI
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install packages
        echo Check your internet connection and try again
        echo.
        pause
        exit /b 1
    )
)
echo Packages installed successfully!
echo.

echo [STEP 5/7] Creating configuration file...
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo Configuration file created from template
    ) else (
        echo ERROR: .env.example file not found
        pause
        exit /b 1
    )
) else (
    echo Configuration file already exists
)
if not exist "logs" (
	mkdir logs
	echo logs directory created
)
echo.

echo [STEP 6/7] Setting up database...
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

echo [STEP 7/7] Creating admin user...
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
