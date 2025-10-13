================================================================================
                    PORTABLE PYTHON INSTALLATION (OPTIONAL)
                         WinPython Bundle Instructions
================================================================================

This folder is for OPTIONAL portable Python installation.

================================================================================
                    DO YOU NEED THIS?
================================================================================

NO - If Python is already installed on your computer or network
YES - If you want a completely portable, no-installation-required package
YES - If deploying to computers without Python installed
YES - If you want zero dependencies

================================================================================
                    WHAT IS WINPYTHON?
================================================================================

WinPython is a portable Python distribution for Windows that:
✓ Requires NO installation
✓ Runs from any location (USB drive, network drive, local folder)
✓ Includes Python + pip (everything needed)
✓ Is completely portable (no registry changes)
✓ Can coexist with other Python installations

================================================================================
                    HOW TO ADD WINPYTHON TO THIS PACKAGE
================================================================================

STEP 1: Download WinPython
---------------------------
Go to: https://github.com/winpython/winpython/releases

Download ONE of these (choose based on your needs):

Option A - MINIMAL (Recommended, ~23 MB):
  File: Winpython64-3.12.10.1dot.exe
  Best for: Deployment packages, network drives

Option B - MINIMAL ZIP (~38 MB):
  File: Winpython64-3.12.10.1dot.zip
  Best for: If you prefer ZIP files

Option C - WITH SPYDER (~630 MB):
  File: Winpython64-3.12.10.1slim.exe or .7z
  Best for: Development environments
  Includes: Spyder IDE, more libraries

STEP 2: Place WinPython Here
-----------------------------
Put the downloaded file (.exe or .zip) in THIS folder:
  portable_python/

Your structure should look like:
  traineeDatabase/
  ├── portable_python/
  │   ├── Winpython64-3.12.10.1dot.exe  ← Downloaded file here
  │   └── README.txt                     ← This file
  ├── wheels/
  ├── FIRST_TIME_SETUP.bat
  └── ...

STEP 3: Done!
-------------
That's it! The setup script will automatically:
✓ Detect the WinPython file
✓ Extract it (if .exe or .zip)
✓ Use it for installation
✓ Install all packages from wheels/ folder

================================================================================
                    AUTOMATIC DETECTION
================================================================================

The FIRST_TIME_SETUP.bat script will automatically detect:
1. WinPython in portable_python/ folder (highest priority)
2. Python configured in PYTHON_PATH.txt
3. Python in system PATH (standard installation)

If WinPython is found, it will:
✓ Extract to portable_python/WPy64-31210/ (if .exe)
✓ Use portable_python/WPy64-31210/python-3.12.10.amd64/python.exe
✓ Install packages offline from wheels/ folder
✓ Complete setup without internet or admin rights

================================================================================
                    MANUAL EXTRACTION (ALTERNATIVE)
================================================================================

If you prefer to extract WinPython manually:

1. Download Winpython64-3.12.10.1dot.exe

2. Run it and extract to:
   traineeDatabase/portable_python/

3. After extraction, you'll have:
   traineeDatabase/
   ├── portable_python/
   │   ├── WPy64-31210/
   │   │   ├── python-3.12.10.amd64/
   │   │   │   ├── python.exe          ← The Python executable
   │   │   │   └── ...
   │   │   └── ...
   │   └── README.txt
   ├── wheels/
   └── ...

4. The setup script will automatically find python.exe in this structure

================================================================================
                    FILE SIZE COMPARISON
================================================================================

DEPLOYMENT PACKAGE WITHOUT WINPYTHON:
  wheels/ folder:              108 MB
  Application code:              5 MB
  Documentation:                 1 MB
  Total:                       114 MB

DEPLOYMENT PACKAGE WITH WINPYTHON (MINIMAL):
  wheels/ folder:              108 MB
  portable_python/:             23 MB  (WinPython minimal .exe)
                          OR    38 MB  (WinPython minimal .zip)
  Application code:              5 MB
  Documentation:                 1 MB
  Total:                       137 MB  (with .exe)
                          OR   152 MB  (with .zip)

DEPLOYMENT PACKAGE WITH WINPYTHON (WITH SPYDER):
  Total:                      ~744 MB  (much larger, not recommended)

================================================================================
                    BENEFITS OF BUNDLING WINPYTHON
================================================================================

FOR END USERS:
✓ Zero Python installation required
✓ Extract zip → double-click setup → done
✓ Works on locked-down corporate PCs
✓ No admin rights needed
✓ No PATH configuration needed
✓ Works from network drives

FOR ADMINISTRATORS:
✓ Single zip file deployment
✓ Guaranteed Python version consistency
✓ No Python version conflicts
✓ Works offline (with bundled wheels)
✓ Portable to any Windows PC
✓ Easy backup and transfer

================================================================================
                    TESTING THE PACKAGE
================================================================================

To test if WinPython is properly bundled:

1. Make sure WinPython file is in portable_python/ folder
2. Run FIRST_TIME_SETUP.bat
3. Look for these messages:
   "[INFO] Portable Python detected in portable_python/"
   "[INFO] Extracting WinPython..." (if using .exe)
   "[INFO] Using portable Python from WinPython"

4. Setup should complete without asking for Python installation

================================================================================
                    FREQUENTLY ASKED QUESTIONS
================================================================================

Q: Do I have to bundle WinPython?
A: No! It's completely optional. Users can install Python normally.

Q: What if I don't bundle WinPython?
A: Users must install Python 3.10-3.13 themselves. Setup works the same way.

Q: Can I use a different Python version?
A: The wheels are built for Python 3.10-3.13. Use WinPython 3.12 for best
   compatibility (works with all bundled wheels).

Q: What if WinPython is outdated?
A: Download the latest "dot" version from GitHub releases. Update this README
   with the new version number.

Q: Can I bundle multiple WinPython versions?
A: Not recommended. Too large. Bundle one version (3.12 recommended) and let
   users with different Python versions use their installed Python.

Q: Does WinPython work on network drives?
A: Yes! That's one of its main benefits. It's designed for portable use.

Q: What about Python 3.13 from WinPython?
A: As of June 2025, WinPython 3.12 is the latest stable. Python 3.13 WinPython
   will be available later. The bundled wheels support both.

Q: Can I use the WinPython "slim" or "full" versions?
A: Yes, but they're much larger (630+ MB). The "dot" minimal version is
   sufficient for this application.

================================================================================
                    DOWNLOAD LINKS
================================================================================

Official WinPython:
  Website: https://winpython.github.io/
  GitHub: https://github.com/winpython/winpython
  Releases: https://github.com/winpython/winpython/releases
  SourceForge: https://sourceforge.net/projects/winpython/files/

Recommended Download for This Application:
  Winpython64-3.12.10.1dot.exe (23 MB)
  Direct link: https://github.com/winpython/winpython/releases/download/8.9.20250628final/Winpython64-3.12.10.1dot.exe

Alternative (ZIP format):
  Winpython64-3.12.10.1dot.zip (38 MB)

================================================================================
                    SUPPORT
================================================================================

If WinPython detection isn't working:
1. Check that the file is in portable_python/ folder
2. Check the filename matches: Winpython64-3.12.10.1dot.exe or .zip
3. Run FIRST_TIME_SETUP.bat and look for detection messages
4. Check PORTABLE_PYTHON.txt for troubleshooting

For more help:
- See HOW_TO_USE.txt for complete setup instructions
- See DEPLOYMENT_README.txt for package overview
- See OFFLINE_INSTALL.txt for wheel installation details

================================================================================
                    END OF README
================================================================================
