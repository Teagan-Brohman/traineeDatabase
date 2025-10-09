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
✓ PRE-BUILT PACKAGES (wheels/ folder - 56 MB)
  - Works OFFLINE without internet connection
  - No C++ build tools required
  - Supports Python 3.11-3.12 (64-bit Windows)

WHAT'S NOT INCLUDED (Will be created automatically):
----------------------------------------------------
✗ Virtual environment (venv/) - Created by FIRST_TIME_SETUP.bat
✗ Database (db.sqlite3) - Created by FIRST_TIME_SETUP.bat
✗ Log files - Created automatically when server runs
✗ Python itself - Must be installed separately

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
IMPORTANT: Python 3.11 or 3.12 (64-bit) required for bundled packages!

Option A: Install Python normally
  - Download Python 3.11 or 3.12 from https://www.python.org/downloads/
  - Check "Add Python to PATH" during installation
  - Must be 64-bit version for offline installation

Option B: Use portable Python
  - Use portable Python 3.11 or 3.12 (64-bit)
  - Edit PYTHON_PATH.txt to point to your portable python.exe
  - See HOW_TO_USE.txt for detailed instructions

Option C: Different Python version (requires internet)
  - If you have Python 3.10 or other versions
  - Setup will download packages from internet (PyPI)
  - Pre-built wheels won't work, but online install will

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

PRE-BUILT PACKAGES (wheels/ folder - 56 MB):
--------------------------------------------
Pre-compiled Python packages for offline installation
✓ Works without internet connection
✓ No C++ build tools required
✓ Python 3.11 & 3.12 (64-bit Windows)

Includes wheels for:
  - numpy-2.3.3 (cp311 & cp312)
  - pandas-2.3.3 (cp311 & cp312)
  - Django-5.2.7
  - openpyxl-3.1.5
  - python-decouple-3.8
  - All other dependencies (12 packages total)

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
✓ Python 3.11 or 3.12 (64-bit) - For offline installation
  OR Python 3.10+ with internet connection
✓ 600 MB free disk space (includes 56 MB wheels)
✓ Network connection (for team access)
✓ Port 8000 available
✓ No C++ build tools required (with bundled wheels)

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
