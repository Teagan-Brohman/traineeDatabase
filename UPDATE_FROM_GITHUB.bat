@echo off
REM ========================================
REM Trainee Tracker - Update from GitHub
REM ========================================
REM This script pulls the latest version from GitHub
REM ========================================

echo.
echo ===============================================
echo    TRAINEE BADGE TRACKER - GitHub Update
echo ===============================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed
    echo.
    echo Please install Git from: https://git-scm.com/download/win
    echo OR use UPDATE_FROM_ZIP.bat instead
    echo.
    pause
    exit /b 1
)

REM Check if this is a git repository
if not exist ".git" (
    echo This is not a Git repository yet
    echo.
    echo [STEP 1/2] Initializing Git repository...
    git init
    if errorlevel 1 (
        echo ERROR: Failed to initialize Git
        pause
        exit /b 1
    )

    echo [STEP 2/2] Connecting to GitHub...
    git remote add origin https://github.com/Teagan-Brohman/traineeDatabase.git
    if errorlevel 1 (
        echo ERROR: Failed to add remote
        pause
        exit /b 1
    )

    echo Git repository initialized!
    echo.
    echo Now pulling latest code...
    echo.
)

echo [STEP 1/5] Creating backup...
set BACKUP_NAME=backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_NAME=%BACKUP_NAME: =0%
mkdir backups\%BACKUP_NAME% 2>nul
copy db.sqlite3 backups\%BACKUP_NAME%\db.sqlite3 >nul 2>&1
copy .env backups\%BACKUP_NAME%\.env >nul 2>&1
echo Database and settings backed up to: backups\%BACKUP_NAME%
echo.

echo [STEP 2/5] Checking for updates...
git fetch origin
if errorlevel 1 (
    echo ERROR: Failed to fetch updates from GitHub
    echo Check your internet connection
    pause
    exit /b 1
)
echo.

echo [STEP 3/5] Pulling latest code...
git pull origin main
if errorlevel 1 (
    echo ERROR: Failed to pull updates
    echo You may have local changes that conflict
    echo.
    pause
    exit /b 1
)
echo Code updated successfully!
echo.

echo [STEP 4/5] Updating dependencies...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    pip install -r requirements.txt --upgrade --quiet
    echo Dependencies updated
) else (
    echo WARNING: Virtual environment not found
    echo Run FIRST_TIME_SETUP.bat to create it
)
echo.

echo [STEP 5/5] Running database migrations...
if exist "venv\Scripts\activate.bat" (
    python manage.py migrate --noinput
    echo Database migrations complete
) else (
    echo WARNING: Skipping migrations - venv not found
)
echo.

echo ===============================================
echo    UPDATE COMPLETE!
echo ===============================================
echo.
echo What was updated:
echo   - Application code (all .py files)
echo   - Templates and static files
echo   - Dependencies (requirements.txt)
echo   - Database schema (migrations)
echo.
echo What was NOT changed:
echo   - Your database (db.sqlite3)
echo   - Your settings (.env)
echo   - Your logs
echo.
echo Backup location: backups\%BACKUP_NAME%
echo.
echo You can now restart the server with START_SERVER.bat
echo.
pause
