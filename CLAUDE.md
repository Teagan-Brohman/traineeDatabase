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
/tracker/<badge_number>/unsign/<task_id>/   -> POST endpoint to remove sign-off
/tracker/bulk-signoff/      -> POST endpoint for bulk operations (JSON)
/tracker/export/            -> Export current cohort to Excel
/tracker/archive/           -> View archived cohorts
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
- `trainee_list.html` - Shows all trainees with progress bars, bulk operations UI
- `trainee_detail.html` - Shows task checklist with inline JavaScript modals for sign-offs
- `archive_list.html` - Shows archived cohorts with search functionality

### Django Template + JavaScript Pattern

**This application uses Django Template Language (DTL) mixed with JavaScript - this is the standard Django approach:**

1. **Files are `.html` Django templates** that combine:
   - Django template tags: `{% extends %}`, `{% for %}`, `{% if %}`
   - Django variables: `{{ trainee.badge_number }}`, `{{ csrf_token }}`
   - HTML markup: `<div>`, `<table>`, `<button>`
   - JavaScript code: `<script>` blocks with client-side logic

2. **Processing flow**:
   - **Server-side**: Django processes the template first, replacing all `{{ }}` and `{% %}` with actual values
   - **Browser receives**: Pure HTML + JavaScript (no Django syntax remains)
   - **Client-side**: JavaScript runs in browser, handles interactions, makes AJAX calls back to Django

3. **Key pattern examples**:
   ```django
   <!-- Django generates the URL -->
   fetch('{% url "bulk_sign_off" %}', {...})

   <!-- Django inserts CSRF token -->
   headers: {'X-CSRFToken': '{{ csrf_token }}'}

   <!-- Django loops to create JavaScript data -->
   {% for task in tasks %}
       taskData.push({id: {{ task.id }}, name: '{{ task.name|escapejs }}'});
   {% endfor %}
   ```

4. **Modal Sign-Off Pattern**: Uses vanilla JavaScript modals (no framework) that:
   - Are created dynamically via `document.createElement()`
   - POST to Django endpoints with CSRF token protection
   - Use AJAX (`fetch`) for bulk operations to avoid page reloads

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
- For JSON endpoints (like bulk_sign_off), return `JsonResponse` instead of redirecting

When working with templates:
- Templates are `.html` files that mix Django Template Language + HTML + JavaScript
- Django processes templates server-side before sending to browser
- JavaScript in templates has access to Django context via template variables
- **Important**: Use `{% url 'view_name' %}` to generate URLs, never hardcode paths
- **Important**: Always include `{{ csrf_token }}` for POST requests from JavaScript
- Use `|escapejs` filter when embedding Django strings in JavaScript: `'{{ value|escapejs }}'`
- Context variables must be passed from views (e.g., `tasks` for bulk operations dropdowns)

## Excel Import Format Expectations

The system expects Excel files structured as:
- Row 1-2: Headers and metadata
- Row 3+: Data rows with badge numbers starting with `#`
- Column A: Badge Number (e.g., `#2523`)
- Column B: Name in "Last, First" format

To import new cohorts, place Excel file in project root and modify `import_data.py` filename reference.

## Bulk Operations Feature

### Overview
Bulk operations allow staff to sign off multiple trainees on one task, or one trainee on multiple tasks simultaneously.

### Backend Implementation

**View**: `tracker/views.py:bulk_sign_off()`
- Accepts JSON POST requests
- Validates user authorization for each task
- Validates scores if required
- Uses database transactions for atomic operations
- Returns JSON response with success/error details

**Request Format**:
```python
{
    "trainee_ids": [1, 2, 3],  # List of trainee IDs
    "task_ids": [5],           # List of task IDs
    "scores": {"5": "95"},     # Dict of task_id -> score
    "notes": "Bulk completion"
}
```

**Response Format**:
```python
{
    "success": true,
    "created": 3,              # New signoffs created
    "updated": 1,              # Existing signoffs updated
    "skipped": [               # Items skipped (with reason)
        {"trainee": "#2523", "task": "Quiz", "reason": "Not authorized"}
    ],
    "errors": []               # Validation errors (causes rollback)
}
```

### Frontend Implementation

**Trainee List** (`tracker/templates/tracker/trainee_list.html`):
- Checkbox column for selecting trainees
- Bulk toolbar appears when selections made
- Modal shows selected trainees and task dropdown
- JavaScript handles selection state and AJAX submission
- Uses `tasks` context variable for task dropdown

**Trainee Detail** (`tracker/templates/tracker/trainee_detail.html`):
- Checkboxes for unsigned, authorized tasks
- Bulk toolbar for multi-task signoff
- Modal with individual score inputs for tasks requiring scores
- JavaScript manages task selection and validation

**Styling** (`tracker/templates/tracker/base.html`):
- `.bulk-toolbar` - Floating action bar
- `.modal-overlay` - Full-screen modal backdrop
- `.bulk-modal` - Wide modal for bulk operations
- `.progress-spinner` - Loading indicator

### Key Design Decisions

1. **Two Use Cases**:
   - **Many trainees, one task**: Common for cohort-wide completions (e.g., orientation)
   - **One trainee, many tasks**: Catching up individual trainees

2. **Authorization**: Every task is validated against `Task.can_user_sign_off()` before processing

3. **Score Handling**:
   - Multi-trainee mode: Single score applies to all
   - Multi-task mode: Individual score inputs for each task requiring scores

4. **Atomic Operations**: All signoffs in a request succeed or all fail (transaction.atomic)

5. **User Feedback**: Shows counts of created/updated/skipped, with detailed error messages

### Testing
Comprehensive test suite in `tracker/tests.py:BulkSignOffTestCase`:
- Multiple trainees, single task
- Single trainee, multiple tasks
- Score validation (required, minimum)
- Authorization enforcement
- Update existing signoffs
- Empty selections
- Authentication requirements
- Invalid JSON handling

See tests for examples of expected behavior and edge cases.
