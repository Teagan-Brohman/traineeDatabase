# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Django web application with two main tracking systems:

1. **Orientation Tracking** - Tracks trainee badge progress through ordered training requirements. Multiple staff members can sign off on tasks, providing an audit trail with timestamps and recorded scores.

2. **Advanced Training** - Tracks ongoing staff training requirements (KP, Escort, ExpSamp, etc.) with expiration dates and authorization controls.

**Key Use Case**: Replaces Excel-based tracking system for reactor training programs where trainees must complete ordered tasks (SOPs, quizzes, clearances) to earn badges, and staff must maintain current training certifications.

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

The application has two parallel tracking systems in `tracker/models.py`:

**Orientation Tracking Models:**
1. **Trainee** - Individual trainees with badge numbers and cohorts
2. **Task** - Ordered training requirements (SOPs, quizzes, procedures)
3. **SignOff** - Junction table linking Trainee + Task with staff approval (unique constraint on trainee+task pair)
4. **StaffProfile** - One-to-one extension of Django User for staff initials

**Advanced Training Models:**
1. **AdvancedStaff** - Staff members requiring ongoing training
2. **AdvancedTrainingType** - Types of training (KP, Escort, ExpSamp, etc.)
3. **AdvancedTraining** - Completion records linking staff to training types

**Critical Design Pattern**:
- Orientation SignOff uses `unique_together = ['trainee', 'task']` meaning each task can only be signed off once per trainee. Updates replace the existing signoff (including who signed and when).
- Advanced Training uses `unique_together = ['staff', 'training_type', 'custom_type']` allowing multiple "Other" training records with different custom types.

### Authentication Flow

- All views require `@login_required` decorator
- Login redirects to `/admin/login/` (reuses Django admin authentication)
- After login, users access `/tracker/` for the main interface
- Admin panel at `/admin/` is for data management only

### URL Structure

**Orientation Tracking:**
```
/                                           -> Redirects to trainee list
/tracker/                                   -> List all trainees (trainee_list view)
/tracker/<badge_number>/                    -> Detail view for one trainee (trainee_detail view)
/tracker/<badge_number>/signoff/<task_id>/  -> POST endpoint to sign off task
/tracker/<badge_number>/unsign/<task_id>/   -> POST endpoint to remove sign-off
/tracker/bulk-signoff/                      -> POST endpoint for bulk operations (JSON)
/tracker/export/                            -> Export current cohort to Excel
/tracker/archive/                           -> View archived cohorts
/tracker/archive/<cohort_id>/               -> View specific archived cohort
```

**Advanced Training:**
```
/tracker/advanced/main/                     -> Main interface with inline editing
/tracker/advanced/<badge_number>/           -> Staff detail view
/tracker/advanced/export/                   -> Excel export (active staff)
/tracker/advanced/export/removed/           -> Excel export (removed staff)
/tracker/advanced/update-training/          -> AJAX POST endpoint for add/edit
/tracker/advanced/delete-training/<id>/     -> AJAX POST endpoint for delete
```

**Admin:**
```
/admin/                                     -> Django admin interface
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

---

## Advanced Training System

The application includes a separate **Advanced Training System** for tracking ongoing staff training requirements beyond initial orientation. This system runs parallel to the trainee orientation tracking with its own models, views, and interface.

### Advanced Training Data Models

**Located in**: `tracker/models.py`

Three interconnected models support advanced training:

1. **AdvancedStaff** - Staff members (separate from trainees)
   - Badge number, name, role (Staff/Grad/Postdoc/Other)
   - `is_active` flag for active vs. removed staff
   - Separate from trainee records

2. **AdvancedTrainingType** - Types of training required
   - Name (e.g., "KP Training", "Escort Training", "ExpSamp Training")
   - Display order
   - `allows_custom_type` flag for "Other Training" categories
   - **Authorization**: `authorized_signers` ManyToMany field restricts who can sign off
   - `can_user_sign_off(user)` method checks authorization

3. **AdvancedTraining** - Completion records
   - Links staff to training type
   - `completion_date` - When training was actually completed
   - `signed_at` - When training was signed off in the system
   - `approver_initials` - Auto-populated from logged-in user
   - `termination_date` - Optional expiration date
   - `custom_type` - For "Other Training" subcategories
   - `is_expired` property and `is_expiring_soon()` method for status

### URL Structure

```
/tracker/advanced/                          -> List view (deprecated, use main)
/tracker/advanced/main/                     -> Main full-featured page with inline editing
/tracker/advanced/removed/                  -> Removed staff list
/tracker/advanced/export/                   -> Excel export (active staff)
/tracker/advanced/export/removed/           -> Excel export (removed staff)
/tracker/advanced/update-training/          -> AJAX endpoint for add/edit
/tracker/advanced/delete-training/<id>/     -> AJAX endpoint for delete
/tracker/advanced/<badge_number>/           -> Staff detail view
```

### Main Interface Features

**View**: `advanced_staff_main` in `tracker/views.py`
**Template**: `tracker/templates/tracker/advanced_staff_main.html`

Key features:
- **Inline editing via modals** - Click any cell to add/edit training
- **Filtering** - By role and status (active/removed/all)
- **Client-side search** - Filter by name or badge number
- **Color-coded status indicators**:
  - ✓ (green) - Current/valid training
  - ⚠️ (yellow) - Expiring soon (within 30 days)
  - ❌ (red) - Expired training
  - + (gray) - No training recorded
- **AJAX operations** - No page reloads for add/edit/delete
- **Authorization enforcement** - Only authorized users can sign off specific training types

### Authorization System

Works identically to orientation tracking tasks:

1. **Admin Configuration**: Go to Django Admin → Advanced Training Types
2. **Set Authorized Signers**: Select specific users, or leave empty to allow all staff
3. **Enforcement**: `update_advanced_training` view checks `training_type.can_user_sign_off(request.user)`
4. **Error Handling**: Returns HTTP 403 with clear error message if unauthorized

### Auto-Population on Sign-Off

When a user signs off advanced training:
- `approver_initials` - Auto-filled from `request.user.staff_profile.initials`
- `signed_at` - Auto-set to current timestamp (`timezone.now()`)
- **Read-only in UI** - User cannot manually edit these fields

This ensures accurate audit trail of who signed off and when.

### Excel Export/Import

**Import Script**: `import_advanced_data.py`
- Reads from `ADV_TrainingStatus_WIP.xlsx`
- Two sheets: "ADV" (active) and "ADV_Removed" (removed)
- Column structure: Badge, Last Name, First Name, Role, then training columns
- Run once during initial setup: `python import_advanced_data.py`

**Export Functions**: `export_advanced_excel()` and `export_advanced_excel_removed()`
- Use same Excel file as template
- Clear existing data and write current database records
- Export all 5 training types with dates, approver initials, termination dates
- Dynamic export button based on status filter in UI

### Navigation Integration

The main navigation bar (in `base.html`) provides system-wide navigation:
- **Orientation Tracking** - Trainee badge tracking
- **Advanced Training** - Staff training tracking
- **Archives** - Historical cohort records

Page-specific actions (exports, filters) remain in page headers.

### Admin Interface Customization

**AdvancedStaffAdmin**:
- Inline display of all training records
- Quick filters by role and active status
- Training status badges in change list

**AdvancedTrainingTypeAdmin**:
- `filter_horizontal` widget for authorized signers
- Displays "All staff" or "{count} staff" for authorization
- Grouped fieldsets for clarity

**AdvancedTrainingAdmin**:
- Autocomplete for staff and training type
- Date hierarchy by completion date
- Ordered by most recent sign-off (`-signed_at`)
- Color-coded status display column

### Common Development Patterns

When modifying advanced training:

1. **Model Changes**: Always create migration after model updates
2. **View Authorization**: Use `training_type.can_user_sign_off(user)` before allowing sign-off
3. **Auto-Population**: Never accept `approver_initials` or `signed_at` from user input
4. **AJAX Responses**: Include full training data in JSON for client-side updates
5. **Template Variables**: Pass `user_initials` in context for read-only display

### Key Differences from Orientation Tracking

| Feature | Orientation Tracking | Advanced Training |
|---------|---------------------|-------------------|
| **Subjects** | Trainees (temporary) | Staff (ongoing) |
| **Tasks/Training** | Ordered sequence | Multiple types |
| **Completion** | One-time badge earning | Recurring/expiring |
| **Status** | Active/Archived by cohort | Active/Removed individuals |
| **Interface** | List + detail pages | Grid with inline editing |
| **Import** | Excel with task columns | Excel with training columns |

Both systems share the same authorization pattern and audit trail approach.

---

## TEMPORARY: Network Drive SQLite Safeguards

**⚠️ IMPORTANT: This section describes TEMPORARY solutions implemented to mitigate risks of running SQLite on a network drive.**

**These safeguards should be REMOVED when migrating to PostgreSQL.**

### Background

SQLite databases are NOT designed for network file systems. Running `db.sqlite3` on a network drive poses serious risks:
- **Database corruption** from concurrent access
- **"Database is locked" errors** even with 2-3 users
- **Data loss** from simultaneous writes
- **Poor performance** due to network latency

The proper solution is migrating to PostgreSQL. However, as a temporary measure, the following safeguards are in place.

### Implemented Safeguards

#### 1. Hybrid Server Lock System (`START_SERVER.bat`)

**Purpose:** Prevent multiple Django servers from running simultaneously and accessing the same database.

**How it works:**
- Creates `SERVER_LOCK` file when server starts
- Contains: computer name, user, start time, IP address
- Heartbeat updater updates timestamp every 60 seconds
- Lock detection uses 3-tier logic:
  - **Lock < 5 minutes old**: Hard block (server definitely running)
  - **Lock 5-10 minutes old**: Ask user to force unlock (might be crashed)
  - **Lock > 10 minutes old**: Auto-cleanup and start (definitely crashed)

**Files involved:**
- `START_SERVER.bat` - Lock creation and detection logic
- `heartbeat_updater.ps1` - Background PowerShell script updating heartbeat
- `SERVER_LOCK` - Lock file (auto-generated, auto-deleted)

**Error messages:**
- "ERROR: Server already running!" → Another computer has active server (< 5 min)
- "WARNING: Server lock detected" → Possibly stale lock (5-10 min), user decides
- "AUTO-RECOVERY: Stale lock detected" → Old lock (> 10 min), auto-cleaned

#### 2. Idle Timeout Monitor (`idle_monitor.py`)

**Purpose:** Automatically shutdown server after period of inactivity to release database lock.

**Configuration:**
- Default timeout: **20 minutes**
- Idle check interval: 5 minutes (300 seconds)
- Fast check interval: 3 seconds
- Configurable via environment variables:
  ```batch
  set IDLE_TIMEOUT_MINUTES=30
  set CHECK_INTERVAL_SECONDS=300
  ```

**How it works (Two-Tier Checking System):**
- **Fast checks (every 3 seconds):**
  - Monitors if `SERVER_LOCK` file still exists
  - Checks if Django server is running (port 8000 detection)
  - Detects forceful window closure within 3 seconds
  - Exits gracefully if server stops unexpectedly

- **Slow checks (every 5 minutes):**
  - Monitors `LAST_ACTIVITY.txt` file updated by Django middleware
  - Calculates idle time since last HTTP request
  - Gracefully shuts down server if idle timeout exceeded
  - Logs activity status (ACTIVE/IDLE)

- **Graceful shutdown:**
  - Cleans up lock file on shutdown
  - Logs reason for exit
  - Prevents orphaned processes

**Key Features:**
- **Stale timestamp prevention:** Initializes `LAST_ACTIVITY.txt` with current time on startup to avoid false timeouts from previous runs
- **Forceful closure detection:** Detects when START_SERVER.bat window is closed and exits within 3 seconds (instead of lingering as orphaned process)
- **Port-based monitoring:** Uses socket connection to port 8000 to detect if Django is still running

**Files involved:**
- `idle_monitor.py` - Python script monitoring activity
- `LAST_ACTIVITY.txt` - Timestamp of last request (auto-generated)
- `tracker/middleware.py` - ActivityTrackerMiddleware updates timestamp
- `idle_monitor.log` - Activity log

#### 3. SQLite Network Optimizations (`settings.py`)

**Purpose:** Configure SQLite for better (but not perfect) concurrent access tolerance.

**Settings applied:**
```python
DATABASES = {
    'default': {
        'OPTIONS': {
            'timeout': 30,  # Wait up to 30 seconds for locks
            'check_same_thread': False,
            'init_command': (
                'PRAGMA journal_mode=WAL;'  # Write-Ahead Logging
                'PRAGMA synchronous=NORMAL;'
                'PRAGMA cache_size=-64000;'  # 64MB cache
                'PRAGMA busy_timeout=30000;'
            ),
        }
    }
}
CONN_MAX_AGE = 0  # No persistent connections
```

**What these do:**
- **WAL mode**: Allows concurrent reads during writes (partial improvement)
- **Busy timeout**: Waits longer before "database locked" error
- **No persistent connections**: Forces fresh connection each request (data consistency)
- **Larger cache**: Reduces disk I/O over network

#### 4. Activity Tracking Middleware (`tracker/middleware.py`)

**Purpose:** Track last HTTP request for idle monitoring.

**Implementation:**
```python
class ActivityTrackerMiddleware:
    def __call__(self, request):
        self.update_activity()  # Write timestamp to file
        return self.get_response(request)
```

**Files involved:**
- `tracker/middleware.py` - Middleware class
- `LAST_ACTIVITY.txt` - Timestamp file
- Registered in `settings.py` MIDDLEWARE list

### User Experience

**Starting Server:**
```
[3/6] Checking for server lock...
[6/6] Starting server...
Lock file created successfully.
Starting heartbeat updater...
Starting idle monitor (timeout: 20 minutes)...

TEMPORARY SAFEGUARDS ACTIVE:
- Server lock prevents multiple instances
- Auto-shutdown after 20 min of inactivity
- Heartbeat updates every 60 seconds
```

**If Another Server Running:**
```
ERROR: Server already running!
Computer: WORKSTATION-05
Started: 2025-01-15 09:00:15
Last heartbeat: 2025-01-15 11:32:45
Lock age: 3 minutes

Please stop the server on WORKSTATION-05 first.
```

**After Crash (Stale Lock):**
```
AUTO-RECOVERY: Stale lock detected
Lock age: 15 minutes
Previous server: WORKSTATION-05

Auto-cleaning and starting new server...
```

#### 5. Server Stop Script (`STOP_SERVER.bat`)

**Purpose:** Gracefully stop Django server and background processes without affecting START_SERVER.bat window.

**How it works:**
- **Django server detection:** Finds process listening on port 8000 using `netstat`, then kills that specific PID
- **Heartbeat detection:** Kills PowerShell process by window title filter
- **Idle monitor detection:** Uses PowerShell with WMI to find python.exe processes running `idle_monitor.py`
- **Cleanup:** Removes `SERVER_LOCK` and `LAST_ACTIVITY.txt` files
- **Safe execution:** Uses proper escaping for parentheses and delayed expansion for variables

**Key Improvements:**
- Uses port-based detection (most reliable for Django server)
- Uses WMI for command-line filtering (avoids complex batch escaping)
- Properly escapes parentheses in echo statements when inside if blocks
- Uses delayed expansion (`!VAR!` instead of `%VAR%`) for correct variable values

**Expected Output:**
```
[1/4] Stopping Django server...
  [OK] Django server stopped (PID: 12345)
[2/4] Stopping heartbeat updater...
  [OK] Heartbeat updater stopped
[3/4] Stopping idle monitor...
  [OK] Idle monitor stopped
[4/4] Cleaning up lock files...
  [OK] Server lock file removed
  [OK] Activity tracking file removed

SUCCESS: Server and background processes stopped
```

### Troubleshooting

**Q: "Database is locked" errors still occurring**
- Only ONE server should run at a time (check `SERVER_LOCK`)
- Verify `db.sqlite3` is on network drive (expected behavior)
- Consider reducing idle timeout to release lock sooner (default is 20 minutes)
- **Long-term:** Migrate to PostgreSQL

**Q: Server auto-shutdown too frequently**
- Increase `IDLE_TIMEOUT_MINUTES` in `idle_monitor.py` (line 29)
- Check `idle_monitor.log` for activity patterns
- Note: Idle timeout prevents lock hogging and is intentionally conservative

**Q: Idle monitor immediately shuts down server on startup**
- This was a bug caused by stale `LAST_ACTIVITY.txt` from previous runs
- **Fixed:** Idle monitor now initializes activity file with current timestamp on startup
- Delete old `LAST_ACTIVITY.txt` manually if issue persists

**Q: Idle monitor doesn't exit when server window closed**
- This was a bug where idle monitor only checked every 5 minutes
- **Fixed:** Now uses fast polling (every 3 seconds) to detect server shutdown
- Idle monitor will exit within 3 seconds of forceful window closure

**Q: Can't start server - lock file won't clear**
- Manually delete `SERVER_LOCK` if server definitely not running
- Check other computers for running servers
- Run `STOP_SERVER.bat` to force cleanup

**Q: STOP_SERVER.bat shows "was unexpected at this time" error**
- This was a syntax error in complex FOR/WMIC loops
- **Fixed:** Simplified to use port-based detection and WMI filtering
- Update to latest version of STOP_SERVER.bat

**Q: STOP_SERVER.bat doesn't find Django server**
- Make sure server is actually running on port 8000
- Check if server was started with `START_SERVER.bat` (not manually)
- Verify no firewall blocking localhost connections

**Q: Multiple servers started accidentally**
- Lock detection only works if `START_SERVER.bat` is used
- Check for `python manage.py runserver` processes manually started
- Run `STOP_SERVER.bat` to kill all servers and clean up

### Files to Remove When Migrating to PostgreSQL

**Delete these files:**
```
heartbeat_updater.ps1
idle_monitor.py
idle_monitor.log (if exists)
SERVER_LOCK (if exists)
LAST_ACTIVITY.txt (if exists)
tracker/middleware.py
```

**Update these files:**

`START_SERVER.bat`:
- Remove lock detection logic (lines 69-157)
- Remove heartbeat/idle monitor launch (lines 167-197)
- Remove cleanup on stop (lines 236-245)
- Remove "TEMPORARY SAFEGUARDS ACTIVE" message

`STOP_SERVER.bat`:
- Remove background process cleanup (lines 37-70)

`settings.py`:
- Remove `ActivityTrackerMiddleware` from MIDDLEWARE
- Remove SQLite-specific OPTIONS and CONN_MAX_AGE
- Update DATABASES to PostgreSQL configuration:
  ```python
  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.postgresql',
          'NAME': 'trainee_tracker',
          'USER': 'postgres',
          'PASSWORD': '<password>',
          'HOST': 'localhost',
          'PORT': '5432',
      }
  }
  CONN_MAX_AGE = 600  # 10 minutes (safe for PostgreSQL)
  ```

`CLAUDE.md`:
- Remove this entire "TEMPORARY: Network Drive SQLite Safeguards" section

### Migration to PostgreSQL Checklist

When ready to migrate from SQLite to PostgreSQL:

- [ ] Install PostgreSQL on server/network
- [ ] Create database: `CREATE DATABASE trainee_tracker;`
- [ ] Create user with permissions
- [ ] Install psycopg2: `pip install psycopg2-binary`
- [ ] Export SQLite data: `python manage.py dumpdata > data.json`
- [ ] Update `settings.py` with PostgreSQL config
- [ ] Migrate schema: `python manage.py migrate`
- [ ] Import data: `python manage.py loaddata data.json`
- [ ] Test application thoroughly
- [ ] Remove all temporary files listed above
- [ ] Update `START_SERVER.bat` and `STOP_SERVER.bat`
- [ ] Remove this section from `CLAUDE.md`
- [ ] Enjoy proper concurrent access! 🎉

### Why These Safeguards Are Not Perfect

**These measures reduce but do NOT eliminate risks:**

1. **Lock file can be deleted manually** - User can bypass protection
2. **Race conditions still possible** - Brief window between lock checks
3. **Network file locking unreliable** - SMB/NFS don't guarantee atomicity
4. **Cache coherency issues** - Django caches data, may serve stale reads
5. **Performance degradation** - Network latency on every database operation
6. **Corruption still possible** - Simultaneous writes, network issues, crashes

**The ONLY proper solution is PostgreSQL** - a client-server database designed for concurrent network access.

These safeguards are a **temporary compromise** to allow network access while planning migration.
