@echo off
setlocal enabledelayedexpansion
REM ========================================
REM Trainee Tracker - Update from ZIP
REM ========================================
REM This script updates the application from a downloaded ZIP file
REM ========================================

echo.
echo ===============================================
echo    TRAINEE BADGE TRACKER - ZIP File Update
echo ===============================================
echo.

REM Prompt for ZIP file location
set /p ZIP_PATH="Enter the full path to the update ZIP file: "

REM Remove quotes if user included them
set ZIP_PATH=%ZIP_PATH:"=%

REM Check if file exists
if not exist "%ZIP_PATH%" (
    echo ERROR: ZIP file not found: %ZIP_PATH%
    echo.
    echo Make sure you:
    echo   1. Downloaded the latest version ZIP from GitHub
    echo   2. Entered the complete path to the file
    echo.
    echo Example: C:\Downloads\traineeDatabase_UPDATE.zip
    echo.
    pause
    exit /b 1
)

echo [STEP 1/6] Creating backup...
set BACKUP_NAME=backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_NAME=%BACKUP_NAME: =0%
mkdir backups\%BACKUP_NAME% 2>nul
copy db.sqlite3 backups\%BACKUP_NAME%\db.sqlite3 >nul 2>&1
copy .env backups\%BACKUP_NAME%\.env >nul 2>&1
echo Database and settings backed up to: backups\%BACKUP_NAME%
echo.

echo [STEP 2/6] Extracting update files...
REM Create temporary extraction directory
mkdir temp_update 2>nul

REM Extract ZIP using PowerShell (built into Windows)
powershell -command "Expand-Archive -Path '%ZIP_PATH%' -DestinationPath 'temp_update' -Force"
if errorlevel 1 (
    echo ERROR: Failed to extract ZIP file
    echo Make sure the ZIP file is not corrupted
    pause
    rmdir /s /q temp_update 2>nul
    exit /b 1
)
echo ZIP file extracted successfully
echo.

echo [STEP 3/6] Updating application files...
REM Update Python code
xcopy /s /y temp_update\tracker\* tracker\ >nul
xcopy /s /y temp_update\trainee_tracker\* trainee_tracker\ >nul
copy /y temp_update\*.py . >nul 2>&1

REM Update batch scripts
copy /y temp_update\*.bat . >nul 2>&1

REM Update documentation
copy /y temp_update\*.txt . >nul 2>&1
copy /y temp_update\*.md . >nul 2>&1

REM Update wheels (if included)
if exist "temp_update\wheels\" (
    xcopy /s /y temp_update\wheels\* wheels\ >nul
    echo Pre-built packages updated
)

REM Update requirements
copy /y temp_update\requirements.txt . >nul 2>&1
copy /y temp_update\requirements-postgres.txt . >nul 2>&1

REM DO NOT copy database, .env, or logs
echo Application code updated successfully
echo.

echo [STEP 4/6] Cleaning up temporary files...
rmdir /s /q temp_update 2>nul
echo.

echo [STEP 5/6] Updating dependencies...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    pip install -r requirements.txt --upgrade --quiet
    echo Dependencies updated
) else (
    echo WARNING: Virtual environment not found
    echo Run FIRST_TIME_SETUP.bat to create it
)
echo.

echo [STEP 6/6] Running database migrations...
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
echo   - Batch scripts
echo   - Documentation
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
