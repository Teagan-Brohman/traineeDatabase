#!/usr/bin/env python
"""
Script to import trainee data from Excel files into the Django database.
Supports importing historical cohorts from the ArchiveChecklists folder.

Usage:
    python import_data.py                           # Import all cohorts from ArchiveChecklists/
    python import_data.py --cohort "Spring 2024"    # Import specific cohort
    python import_data.py --file custom.xlsx --cohort "Summer 2023"  # Custom file
    python import_data.py --skip-existing           # Skip trainees that already exist
"""

import os
import sys
import argparse
import re
import django
from pathlib import Path

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trainee_tracker.settings')
django.setup()

from tracker.models import Task, Trainee, Cohort

class ImportStats:
    """Track import statistics"""
    def __init__(self):
        self.cohorts_created = 0
        self.cohorts_existing = 0
        self.trainees_created = 0
        self.trainees_skipped = 0
        self.errors = []

    def print_summary(self):
        print("\n" + "=" * 60)
        print("IMPORT SUMMARY")
        print("=" * 60)
        print(f"Cohorts created:       {self.cohorts_created}")
        print(f"Cohorts existing:      {self.cohorts_existing}")
        print(f"Trainees created:      {self.trainees_created}")
        print(f"Trainees skipped:      {self.trainees_skipped}")
        if self.errors:
            print(f"\nErrors encountered:    {len(self.errors)}")
            for error in self.errors[:5]:  # Show first 5 errors
                print(f"  - {error}")
            if len(self.errors) > 5:
                print(f"  ... and {len(self.errors) - 5} more")
        print("=" * 60)


def parse_cohort_name(cohort_str):
    """
    Parse cohort string into year and semester.
    Examples: "Spring 2024" -> (2024, "Spring"), "Fall 2023" -> (2023, "Fall")
    """
    parts = cohort_str.strip().split()
    if len(parts) != 2:
        raise ValueError(f"Invalid cohort format: '{cohort_str}'. Expected 'Season Year'")

    semester = parts[0].capitalize()
    if semester not in ['Spring', 'Fall']:
        raise ValueError(f"Invalid semester: '{semester}'. Must be 'Spring' or 'Fall'")

    try:
        year = int(parts[1])
    except ValueError:
        raise ValueError(f"Invalid year: '{parts[1]}'. Must be a number")

    return year, semester


def get_or_create_cohort(cohort_name, stats):
    """
    Get or create a Cohort object from a cohort name string.
    """
    try:
        year, semester = parse_cohort_name(cohort_name)
    except ValueError as e:
        stats.errors.append(f"Failed to parse cohort '{cohort_name}': {e}")
        return None

    cohort, created = Cohort.objects.get_or_create(
        name=cohort_name,
        defaults={
            'year': year,
            'semester': semester,
            'semester_order': 2 if semester == 'Fall' else 1,
        }
    )

    if created:
        stats.cohorts_created += 1
        print(f"  ✓ Created cohort: {cohort_name}")
    else:
        stats.cohorts_existing += 1
        print(f"  - Cohort already exists: {cohort_name}")

    return cohort


def extract_cohort_from_filename(filename):
    """
    Extract cohort name from Excel filename.
    Example: "Check list Orientation Fall 2024.xlsx" -> "Fall 2024"
    """
    # Pattern: Check list Orientation [Season] [Year].xlsx
    pattern = r'Check list Orientation (Spring|Fall) (\d{4})'
    match = re.search(pattern, filename, re.IGNORECASE)

    if match:
        semester = match.group(1).capitalize()
        year = match.group(2)
        return f"{semester} {year}"

    return None


def import_trainees_from_excel(excel_file, cohort_name, stats, skip_existing=False):
    """
    Import trainees from an Excel file and link them to the specified cohort.
    """
    try:
        import pandas as pd
    except ImportError:
        stats.errors.append("pandas not installed. Run: pip install pandas openpyxl")
        return

    if not os.path.exists(excel_file):
        stats.errors.append(f"File not found: {excel_file}")
        return

    print(f"\nProcessing: {os.path.basename(excel_file)}")
    print(f"Cohort: {cohort_name}")

    # Get or create the cohort
    cohort = get_or_create_cohort(cohort_name, stats)
    if not cohort:
        return

    try:
        # Read Excel file
        df = pd.read_excel(excel_file)

        imported = 0
        skipped = 0

        # Process each row
        for index, row in df.iterrows():
            # Skip header rows (first 3 rows)
            if index < 3:
                continue

            badge_num = str(row.iloc[0]).strip()
            name = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else None

            # Skip if badge number is invalid
            if not badge_num or badge_num == 'nan' or not badge_num.startswith('#'):
                continue

            if name and name != 'nan':
                # Parse name (format: "Last, First")
                if ',' in name:
                    last_name, first_name = name.split(',', 1)
                    last_name = last_name.strip()
                    first_name = first_name.strip()
                else:
                    first_name = name
                    last_name = ""

                # Check if trainee already exists
                if skip_existing and Trainee.objects.filter(badge_number=badge_num).exists():
                    skipped += 1
                    continue

                trainee, created = Trainee.objects.get_or_create(
                    badge_number=badge_num,
                    defaults={
                        'first_name': first_name,
                        'last_name': last_name,
                        'cohort': cohort,
                        'is_active': True
                    }
                )

                if created:
                    imported += 1
                    stats.trainees_created += 1
                else:
                    skipped += 1
                    stats.trainees_skipped += 1

        print(f"  → Imported: {imported} trainees")
        if skipped > 0:
            print(f"  → Skipped:  {skipped} trainees (already exist)")

    except Exception as e:
        error_msg = f"Error importing from {os.path.basename(excel_file)}: {e}"
        stats.errors.append(error_msg)
        print(f"  ✗ {error_msg}")


def import_tasks():
    """Import standard training tasks"""
    print("\nImporting Standard Tasks...")
    print("-" * 60)

    tasks = [
        (1, "Onboarding Process Brief", "Onboarding", False),
        (2, "Police Clearance Form", "Security", False),
        (3, "Document Release Form/NDA", "Documentation", False),
        (4, "U.S. Citizen / ID Check", "Security", False),
        (5, "Read SOP's 208, 210", "Training", False),
        (6, "Read SOP 501 A&B", "Training", False),
        (7, "Read SOP's 505, 506, 508, 509, 510", "Training", False),
        (8, "Read SOP's 600, 601", "Training", False),
        (9, "Onboarding Tour", "Training", False),
        (10, "Onboarding Tour Quiz", "Assessment", True),
        (11, "Read R.G. 8.13, R.G. 8.29", "Safety", False),
        (12, "ALARA Statement", "Safety", False),
        (13, "Radiation Safety PowerPoint & Video", "Safety", False),
        (14, "Reg Guides 8.13 / 8.29 Quiz", "Assessment", True),
        (15, "Review Deficiencies", "Assessment", False),
    ]

    created_count = 0
    existing_count = 0

    for order, name, category, requires_score in tasks:
        task, created = Task.objects.get_or_create(
            order=order,
            defaults={
                'name': name,
                'category': category,
                'requires_score': requires_score,
                'is_active': True
            }
        )
        if created:
            created_count += 1
            print(f"  ✓ Created task #{order}: {name}")
        else:
            existing_count += 1

    print(f"\nTasks: {created_count} created, {existing_count} already existed")


def find_excel_files(directory):
    """Find all Excel files in the specified directory"""
    excel_files = []
    path = Path(directory)

    if not path.exists():
        return []

    for file in path.glob("*.xlsx"):
        cohort_name = extract_cohort_from_filename(file.name)
        if cohort_name:
            excel_files.append((str(file), cohort_name))

    # Sort by year and semester
    excel_files.sort(key=lambda x: (
        int(x[1].split()[1]),  # year
        0 if 'Spring' in x[1] else 1  # Spring before Fall
    ))

    return excel_files


def main():
    parser = argparse.ArgumentParser(
        description='Import trainee data from Excel files into the database.'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='Path to a specific Excel file to import'
    )
    parser.add_argument(
        '--cohort',
        type=str,
        help='Cohort name (e.g., "Spring 2024"). Required if --file is specified.'
    )
    parser.add_argument(
        '--skip-existing',
        action='store_true',
        help='Skip trainees that already exist in the database'
    )
    parser.add_argument(
        '--no-tasks',
        action='store_true',
        help='Skip importing standard tasks'
    )

    args = parser.parse_args()

    stats = ImportStats()

    print("=" * 60)
    print("TRAINEE DATA IMPORT TOOL")
    print("=" * 60)

    # Import tasks first (unless skipped)
    if not args.no_tasks:
        import_tasks()

    print("\nImporting Trainees...")
    print("-" * 60)

    # Mode 1: Import specific file
    if args.file:
        if not args.cohort:
            print("Error: --cohort is required when using --file")
            sys.exit(1)

        import_trainees_from_excel(args.file, args.cohort, stats, args.skip_existing)

    # Mode 2: Import specific cohort from ArchiveChecklists
    elif args.cohort:
        # Find the file for this cohort
        excel_files = find_excel_files('ArchiveChecklists')
        matching_file = None

        for file_path, cohort_name in excel_files:
            if cohort_name.lower() == args.cohort.lower():
                matching_file = file_path
                break

        if matching_file:
            import_trainees_from_excel(matching_file, args.cohort, stats, args.skip_existing)
        else:
            print(f"Error: No file found for cohort '{args.cohort}' in ArchiveChecklists/")
            sys.exit(1)

    # Mode 3: Import all cohorts from ArchiveChecklists
    else:
        excel_files = find_excel_files('ArchiveChecklists')

        if not excel_files:
            print("No Excel files found in ArchiveChecklists/ directory")
            print("\nMake sure Excel files follow the naming pattern:")
            print("  Check list Orientation [Season] [Year].xlsx")
            sys.exit(1)

        print(f"Found {len(excel_files)} cohort file(s) in ArchiveChecklists/")
        print()

        for file_path, cohort_name in excel_files:
            import_trainees_from_excel(file_path, cohort_name, stats, args.skip_existing)

    # Print summary
    stats.print_summary()

    print("\nNext steps:")
    print("1. Start server: python manage.py runserver 0.0.0.0:8000")
    print("2. Go to http://localhost:8000/admin")
    print("3. Set current cohort override if needed (Cohorts section)")
    print("4. Create staff user accounts")
    print("5. View trainees at http://localhost:8000/tracker/")


if __name__ == '__main__':
    main()
