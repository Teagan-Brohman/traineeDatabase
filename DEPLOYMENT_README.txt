================================================================================
                    TRAINEE BADGE TRACKER - DEPLOYMENT PACKAGE
                              Version 1.0
================================================================================

CONTENTS OF THIS PACKAGE:
------------------------
This zip file contains everything needed to deploy the Trainee Badge Tracker
application on a network drive or local computer.

WHAT'S INCLUDED:
---------------
✓ Django web application (all Python code)
✓ Database migrations (ready to set up database)
✓ HTML templates (user interface)
✓ Excel import/export functionality
✓ Batch scripts for easy Windows setup
✓ Complete documentation
✓ Sample Excel templates
✓ Test suite (28 comprehensive tests)
✓ PRE-BUILT PACKAGES (wheels/ folder - 108 MB)
  - Works OFFLINE without internet connection
  - No C++ build tools required
  - Supports Python 3.10, 3.11, 3.12, 3.13 (64-bit Windows)
  - Includes PostgreSQL support (psycopg2-binary)
✓ PORTABLE PYTHON FOLDER (portable_python/)
  - Structure ready for WinPython bundle
  - Instructions in portable_python/README.txt
  - Optional - add Winpython64-3.12.10.1dot.exe (23 MB) for zero-dependency setup
  - Makes package completely self-contained

WHAT'S NOT INCLUDED (Will be created automatically):
----------------------------------------------------
✗ Virtual environment (venv/) - Created by FIRST_TIME_SETUP.bat
✗ Database (db.sqlite3) - Created by FIRST_TIME_SETUP.bat
✗ Log files - Created automatically when server runs
✗ Python itself - Optional (can bundle WinPython or install separately)

================================================================================
                              QUICK START
================================================================================

STEP 1: EXTRACT THIS ZIP FILE
------------------------------
Extract all files to your desired location:
  - Network drive: \\server\share\TraineeTracker\
  - Local drive: C:\TraineeTracker\
  - USB drive: E:\TraineeTracker\

STEP 2: READ THE DOCUMENTATION
-------------------------------
After extracting, open and read in this order:
  1. START_HERE.txt - Overview and file guide
  2. HOW_TO_USE.txt - Complete beginner-friendly instructions
  3. QUICKSTART.md - Technical quick start guide

STEP 3: SETUP PYTHON (If needed)
---------------------------------
You have THREE options (choose one):

Option A: Bundle WinPython (ZERO DEPENDENCIES - Recommended for deployment)
  - Download Winpython64-3.12.10.1dot.exe (23 MB) from:
    https://github.com/winpython/winpython/releases
  - Place in portable_python/ folder
  - No Python installation required
  - Works completely offline
  - No admin rights needed
  - See portable_python/README.txt for details

Option B: Install Python normally (If already installed or prefer standard install)
  - Download Python 3.10-3.13 (64-bit) from https://www.python.org/downloads/
  - Check "Add Python to PATH" during installation
  - Works offline with bundled wheels

Option C: Use existing portable Python (If you already have one)
  - Edit PYTHON_PATH.txt to point to your portable python.exe
  - See HOW_TO_USE.txt for detailed instructions
  - Works offline with bundled wheels

STEP 4: RUN FIRST TIME SETUP
-----------------------------
Double-click: FIRST_TIME_SETUP.bat
  - Creates virtual environment
  - Installs all dependencies
  - Sets up database
  - Creates admin account

STEP 5: START THE SERVER
-------------------------
Double-click: START_SERVER.bat
  - Server starts automatically
  - Access at http://localhost:8000
  - Share IP address with team for network access

================================================================================
                            FILE MANIFEST
================================================================================

BATCH SCRIPTS (Double-click to run):
------------------------------------
FIRST_TIME_SETUP.bat - Run once for initial setup
START_SERVER.bat - Start the application server
STOP_SERVER.bat - Force stop the server if needed

DOCUMENTATION (Read these!):
---------------------------
START_HERE.txt - Start here! Overview and navigation
HOW_TO_USE.txt - Complete beginner-friendly guide
OFFLINE_INSTALL.txt - Offline installation details
QUICKSTART.md - Quick technical setup guide
README.md - Full technical documentation
CLAUDE.md - Developer/architecture documentation
POSTGRESQL_SETUP.md - Database migration guide
WINDOWS_INSTALL_FIX.txt - Windows compatibility notes
FUTURE_IMPROVEMENTS.md - Planned features (Phase 3 & 4)

CONFIGURATION FILES:
-------------------
PYTHON_PATH.txt - Configure portable Python (optional)
.env.example - Environment variable template
requirements.txt - Python package dependencies
requirements-postgres.txt - Optional PostgreSQL support
.gitignore - Git ignore rules

PRE-BUILT PACKAGES (wheels/ folder - 108 MB):
---------------------------------------------
Pre-compiled Python packages for offline installation
✓ Works without internet connection
✓ No C++ build tools required
✓ Python 3.10, 3.11, 3.12, 3.13 (64-bit Windows)

Includes wheels for (22 files total):
  - numpy-2.2.6 (cp310, cp311, cp312, cp313)
  - pandas-2.2.3 (cp310, cp311, cp312, cp313)
  - psycopg2-binary-2.9.10 (cp310, cp311, cp312, cp313) - PostgreSQL support
  - Django-5.2.7 (universal)
  - openpyxl-3.1.5 (universal)
  - python-decouple-3.8 (universal)
  - All other dependencies (10 universal wheels)

PORTABLE PYTHON FOLDER (portable_python/):
------------------------------------------
Ready for WinPython bundle (optional)
✓ Add Winpython64-3.12.10.1dot.exe (~23 MB) for complete portability
✓ See portable_python/README.txt for download instructions
✓ Makes package 100% self-contained with zero dependencies
✓ Automatically detected and extracted by setup script

APPLICATION FILES:
-----------------
manage.py - Django management script
import_data.py - Excel import utility

trainee_tracker/ - Django project configuration
  ├── settings.py - Application settings
  ├── urls.py - URL routing
  ├── wsgi.py - WSGI configuration
  └── asgi.py - ASGI configuration

tracker/ - Main application code
  ├── models.py - Database models
  ├── views.py - View logic
  ├── admin.py - Admin interface
  ├── urls.py - App URL routing
  ├── tests.py - Test suite (28 tests)
  ├── exceptions.py - Custom exceptions
  ├── migrations/ - Database migrations (14 files)
  └── templates/ - HTML templates (4 files)

EXCEL TEMPLATES:
---------------
Check list Orientation Blank.xlsx - Export template
Check list Orientation Fall 2025.xlsx - Sample data
Check list Trainees Fall 2025.xlsx - Sample data
Check list Orientation Blank - Copy.xlsx - Backup template

================================================================================
                          SYSTEM REQUIREMENTS
================================================================================

SERVER COMPUTER (Running START_SERVER.bat):
-------------------------------------------
✓ Windows 7 or higher
✓ Python 3.10-3.13 (64-bit) - For offline installation with bundled wheels
  OR use bundled WinPython (no Python installation required)
  OR any Python 3.10+ with internet connection
✓ 750 MB free disk space
  - 108 MB wheels
  - ~23 MB WinPython (if bundled)
  - ~600 MB for venv and application
✓ Network connection (for team access, not required for setup if using wheels)
✓ Port 8000 available
✓ No C++ build tools required
✓ No admin rights required (with WinPython)

CLIENT COMPUTERS (Accessing via browser):
-----------------------------------------
✓ Any operating system (Windows, Mac, Linux)
✓ Modern web browser (Chrome, Firefox, Edge, Safari)
✓ Network access to server computer
✓ No software installation needed

================================================================================
                            IMPORTANT NOTES
================================================================================

SECURITY:
--------
⚠ The included .env.example has a GENERATED secret key
⚠ For production, edit .env and set DEBUG=False
⚠ Use strong passwords for admin accounts
⚠ Don't share admin credentials

BACKUP:
------
⚠ BACKUP db.sqlite3 regularly!
⚠ This file contains all your data
⚠ Copy it to a safe location daily/weekly
⚠ Store backups in multiple locations

NETWORK DRIVE:
-------------
⚠ Only ONE person should run START_SERVER.bat at a time
⚠ Everyone else accesses via web browser
⚠ Server computer must stay on for team access
⚠ Windows Firewall may need to allow Python

UPDATES:
-------
⚠ When updating the application, backup database first
⚠ Run FIRST_TIME_SETUP.bat after updating
⚠ This ensures migrations are applied

================================================================================
                              SUPPORT
================================================================================

COMMON ISSUES:
-------------
Issue: "Python not found"
Fix: Install Python 3.11/3.12 or configure PYTHON_PATH.txt

Issue: "Failed to install packages" or "vswhere.exe not found"
Fix: Use Python 3.11 or 3.12 (64-bit), or enable internet for PyPI

Issue: "Offline installation failed" warning
Fix: Python version mismatch - will auto-fallback to online install

Issue: Can't access from other computers
Fix: Check firewall, use correct IP, ensure server is running

Issue: Database locked
Fix: Only run one server at a time

Issue: Port 8000 in use
Fix: Stop other servers or change port in START_SERVER.bat

DOCUMENTATION:
-------------
All documentation is included in this package:
  - HOW_TO_USE.txt - For non-technical users
  - QUICKSTART.md - For technical users
  - README.md - Complete technical reference
  - CLAUDE.md - Architecture and development guide
  - RELEASE.md - Guide for publishing updates (for maintainers)

================================================================================
                        UPDATING THE APPLICATION
================================================================================

This application supports easy updates while preserving your data!

GitHub Repository: https://github.com/Teagan-Brohman/traineeDatabase

UPDATE METHODS:
--------------

Method 1: Git-Based Updates (Recommended for technical users)
  Script: UPDATE_FROM_GITHUB.bat
  Requirements: Git installed
  How it works:
    - Pulls latest code from GitHub automatically
    - Backs up database and settings before updating
    - Updates dependencies and runs migrations
    - Fast and convenient

Method 2: ZIP File Updates (For non-technical users)
  Script: UPDATE_FROM_ZIP.bat
  Requirements: Downloaded update ZIP file
  How it works:
    - Extracts update files from ZIP
    - Backs up database and settings before updating
    - Updates dependencies and runs migrations
    - No Git knowledge required

WHAT GETS PRESERVED:
-------------------
✓ Database (db.sqlite3) - All your trainee data
✓ Settings (.env) - Your configuration
✓ Logs - Application logs
✓ Backups - Previous backups

WHAT GETS UPDATED:
-----------------
✓ Application code - Bug fixes and new features
✓ Templates - UI improvements
✓ Dependencies - Package updates
✓ Database schema - Automatic migrations
✓ Documentation - Updated guides

BACKUP STRATEGY:
---------------
Both update scripts automatically create timestamped backups:
  Location: backups/backup_YYYYMMDD_HHMMSS/
  Contents: db.sqlite3, .env

To restore from backup:
  1. Navigate to backups/ folder
  2. Find the backup you want (sorted by date/time)
  3. Copy db.sqlite3 back to application folder
  4. Copy .env if settings were changed
  5. Restart server

VERSION TRACKING:
----------------
Check current version: Open version.txt file
Latest version: https://github.com/Teagan-Brohman/traineeDatabase/releases/latest

TROUBLESHOOTING UPDATES:
-----------------------

Issue: "Git not found" error
Fix: Install Git from https://git-scm.com/download/win
     OR use UPDATE_FROM_ZIP.bat instead

Issue: "Authentication failed" during Git update
Fix: Set up GitHub credentials or use UPDATE_FROM_ZIP.bat

Issue: Merge conflicts during Git update
Fix: User has local changes. Backup changes, delete .git folder,
     re-run UPDATE_FROM_GITHUB.bat for fresh start

Issue: Update completed but changes not visible
Fix: 1. Restart the server (START_SERVER.bat)
     2. Clear browser cache (Ctrl+F5)

Issue: Database migration fails
Fix: 1. Check backups/ folder for backup
     2. Restore backup if needed
     3. Report issue on GitHub

FOR MAINTAINERS:
---------------
Publishing updates: See RELEASE.md for complete release process
Creating releases: Use GitHub Releases with version tags (v1.0.0, v1.1.0, etc.)
Update checklist: See RELEASE.md pre-release checklist

================================================================================
                            VERSION HISTORY
================================================================================

Version 1.0 (Current)
--------------------
✓ Phase 1 & 2 improvements implemented
  - Environment-based configuration
  - Database indexes for performance
  - Comprehensive test suite (28 tests)
  - PostgreSQL support
  - N+1 query optimizations
  - Structured logging
  - Custom exceptions

✓ Network drive deployment ready
  - Portable Python support
  - Easy batch file launchers
  - Beginner-friendly documentation
  - Multi-section Excel export fix
  - Pre-built wheels for offline installation (56 MB)
  - No C++ build tools required
  - Python 3.11-3.12 support

✓ Core features
  - 15 training tasks
  - Multi-cohort support
  - Sign-off workflow with audit trail
  - Authorized signers per task
  - Score validation for quizzes
  - Excel import/export
  - Progress tracking
  - Archive functionality

================================================================================
                          GETTING STARTED
================================================================================

Ready to deploy? Follow these steps:

1. Extract this zip to your desired location
2. Read START_HERE.txt
3. Follow instructions in HOW_TO_USE.txt
4. Run FIRST_TIME_SETUP.bat
5. Run START_SERVER.bat
6. Access http://localhost:8000

Questions? Check HOW_TO_USE.txt first!

================================================================================
                            END OF README
================================================================================
