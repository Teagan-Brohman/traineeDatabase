#!/usr/bin/env python3
"""
Creates a deployment zip file for the trainee database application.
Excludes development files and directories.
"""

import zipfile
import os
from pathlib import Path

def should_exclude(path):
    """Check if a path should be excluded from the deployment zip."""
    exclude_patterns = [
        '.git',
        '__pycache__',
        '.pyc',
        'venv',
        '.env',
        '.claude',
        'logs',
        '.log',
        'create_deployment_zip.py',  # Don't include this script itself
    ]

    path_str = str(path)

    # Check if any exclude pattern is in the path
    for pattern in exclude_patterns:
        if pattern in path_str:
            return True

    return False

def create_deployment_zip():
    """Create the deployment zip file."""
    zip_filename = 'traineeDatabase_DEPLOYMENT.zip'
    project_root = Path('.')

    print(f"Creating {zip_filename}...")
    print("Excluding: .git, __pycache__, venv, .env, .claude, logs")

    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        file_count = 0

        # Walk through all files in the project
        for root, dirs, files in os.walk('.'):
            # Convert to Path for easier manipulation
            root_path = Path(root)

            # Skip if the directory itself should be excluded
            if should_exclude(root_path):
                continue

            # Filter out excluded directories to prevent os.walk from descending into them
            dirs[:] = [d for d in dirs if not should_exclude(root_path / d)]

            # Add each file
            for file in files:
                file_path = root_path / file

                if not should_exclude(file_path):
                    # Add to zip with relative path
                    arcname = str(file_path)
                    zipf.write(file_path, arcname)
                    file_count += 1

                    # Print progress every 10 files
                    if file_count % 10 == 0:
                        print(f"  Added {file_count} files...")

    # Get final file size
    size_mb = os.path.getsize(zip_filename) / (1024 * 1024)

    print(f"\n✓ Successfully created {zip_filename}")
    print(f"  Total files: {file_count}")
    print(f"  File size: {size_mb:.2f} MB")
    print(f"\nThis zip contains everything needed for deployment:")
    print("  - Django application code")
    print("  - Database file (db.sqlite3)")
    print("  - Templates and static files")
    print("  - Documentation")
    print("  - Windows batch files")
    print("  - Python wheels for offline installation")
    print("  - Sample Excel files")

if __name__ == '__main__':
    create_deployment_zip()
