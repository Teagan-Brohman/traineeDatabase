# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Django web application for tracking trainee badge progress through training requirements. Multiple staff members can sign off on tasks, providing an audit trail with timestamps and recorded scores.

**Key Use Case**: Replaces Excel-based tracking system for reactor training programs where trainees must complete ordered tasks (SOPs, quizzes, clearances) to earn badges.

## Development Environment Setup

```bash
# Activate virtual environment (ALWAYS do this first)
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Database operations
python manage.py makemigrations
python manage.py migrate

# Create admin account
python manage.py createsuperuser

# Run development server (local only)
python manage.py runserver

# Run development server (network accessible)
python manage.py runserver 0.0.0.0:8000
```

## Application Architecture

### Core Data Model Relationships

The application uses four interconnected models in `tracker/models.py`:

1. **Trainee** - Individual trainees with badge numbers and cohorts
2. **Task** - Ordered training requirements (SOPs, quizzes, procedures)
3. **SignOff** - Junction table linking Trainee + Task with staff approval (unique constraint on trainee+task pair)
4. **StaffProfile** - One-to-one extension of Django User for staff initials

**Critical Design Pattern**: SignOff uses `unique_together = ['trainee', 'task']` meaning each task can only be signed off once per trainee. Updates replace the existing signoff (including who signed and when).

### Authentication Flow

- All views require `@login_required` decorator
- Login redirects to `/admin/login/` (reuses Django admin authentication)
- After login, users access `/tracker/` for the main interface
- Admin panel at `/admin/` is for data management only

### URL Structure

```
/                           -> Redirects to trainee list
/tracker/                   -> List all trainees (trainee_list view)
/tracker/<badge_number>/    -> Detail view for one trainee (trainee_detail view)
/tracker/<badge_number>/signoff/<task_id>/  -> POST endpoint to sign off task
/admin/                     -> Django admin interface
```

### Admin Interface Customization

The admin panel (`tracker/admin.py`) heavily customizes the Django admin:

- **TraineeAdmin**: Shows inline SignOffs for each trainee, displays progress percentage
- **SignOffAdmin**: Auto-populates `signed_by` field with current user on save
- **UserAdmin**: Extended with StaffProfile inline to add initials during user creation
- Progress percentages calculated via `Trainee.get_progress_percentage()` method

### View Logic Pattern

`trainee_detail` view uses an optimization pattern:
1. Fetch all tasks (ordered by `order` field)
2. Fetch all signoffs for the trainee
3. Build a dictionary `{task_id: signoff}` for O(1) lookup
4. Combine into `task_progress` list of dicts for template

This avoids N+1 query problem when rendering task lists.

## Data Import Workflow

`import_data.py` is a standalone script (not a management command) that:
1. Uses `django.setup()` to bootstrap Django outside of normal execution
2. Imports predefined tasks (15 standard reactor training requirements)
3. Reads Excel files with specific format expectations:
   - First column: Badge numbers (must start with `#`)
   - Second column: Names in "Last, First" format
   - First 3 rows are headers (skipped)

**When to run**: After initial database setup but before trainees/staff start using the system.

## Database

Uses SQLite (`db.sqlite3`) stored in project root. For production or network deployment, this file must be accessible to all users.

**Backup**: Simply copy `db.sqlite3` file. No additional tooling required.

## Template Structure

Templates in `tracker/templates/tracker/`:
- `base.html` - Contains all CSS (no external stylesheets), provides layout structure
- `trainee_list.html` - Shows all trainees with progress bars
- `trainee_detail.html` - Shows task checklist with inline JavaScript modal for sign-offs

**Modal Sign-Off Pattern**: Uses vanilla JavaScript modal (no framework) that POSTs to sign-off endpoint with CSRF token.

## Settings Configuration

Key settings in `trainee_tracker/settings.py`:

- `ALLOWED_HOSTS = ['*']` - Currently wide open for development; restrict for production
- `TIME_ZONE = 'America/Chicago'` - Adjust based on deployment location
- `LOGIN_URL = '/admin/login/'` - Reuses admin login rather than custom auth
- `DEBUG = True` - Must be set to `False` for production
- Single app architecture: Only `tracker` app in `INSTALLED_APPS`

## Network Deployment Notes

This application is designed to run on a shared network drive:
1. Server must run with `0.0.0.0` binding to listen on all network interfaces
2. Users access via `http://<server-ip>:8000`
3. Database file (`db.sqlite3`) handles concurrent reads but SQLite has write concurrency limitations
4. For high-traffic scenarios, consider migrating to PostgreSQL via `DATABASES` setting change

## Key Constraints and Business Logic

1. **Task Order Matters**: Tasks have an `order` field determining display sequence (matches training progression)
2. **Active Flags**: Both Trainee and Task have `is_active` boolean to "soft delete" without losing history
3. **Sign-Off Immutability**: SignOffs track `signed_at` timestamp automatically; cannot be backdated
4. **Progress Calculation**: Progress is calculated on-demand (not cached) by counting distinct task signoffs vs total active tasks
5. **Quiz Scores**: Tasks with `requires_score=True` expect a score field in signoff; displayed conditionally in UI

## Common Development Patterns

When adding new models, always:
1. Add to `tracker/models.py`
2. Register in `tracker/admin.py` with `@admin.register(ModelName)` decorator
3. Run `makemigrations` and `migrate`
4. Update `import_data.py` if data should be seeded

When modifying views:
- All views should use `@login_required` decorator
- Use `get_object_or_404` for lookups by badge_number or task_id
- Add success messages via `messages.success()` for user feedback
- Always redirect after POST (POST-Redirect-GET pattern)

## Excel Import Format Expectations

The system expects Excel files structured as:
- Row 1-2: Headers and metadata
- Row 3+: Data rows with badge numbers starting with `#`
- Column A: Badge Number (e.g., `#2523`)
- Column B: Name in "Last, First" format

To import new cohorts, place Excel file in project root and modify `import_data.py` filename reference.
