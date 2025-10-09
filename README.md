# Trainee Badge Tracker

A Django web application for tracking trainee progress through badge requirements. This system allows multiple staff members to sign off on tasks and provides an easy-to-use interface for monitoring trainee progress.

## Features

- **Trainee Management**: Track multiple trainees with badge numbers and cohorts
- **Task Tracking**: Define tasks/requirements for badge completion
- **Multi-User Sign-Offs**: Staff members can sign off on completed tasks
- **Progress Monitoring**: Visual progress bars showing completion percentage
- **Quiz Scores**: Support for recording quiz/test scores
- **Audit Trail**: Track who signed off and when
- **Admin Interface**: Easy-to-use Django admin for data management
- **Network Access**: Can be accessed across a shared network drive

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. **Navigate to the project directory:**
   ```bash
   cd /path/to/traineeDatabase
   ```

2. **Create and activate virtual environment:**
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a superuser (admin account):**
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to set username, email, and password.

5. **Run the development server:**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

6. **Access the application:**
   - Main interface: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

## Initial Setup

### 1. Create Staff Accounts
1. Go to the admin panel (http://localhost:8000/admin)
2. Navigate to "Users" and click "Add User"
3. Create user accounts for each staff member
4. After creating the user, edit them and add their Staff Profile with initials

### 2. Add Tasks
1. In the admin panel, navigate to "Tasks"
2. Click "Add Task" and fill in:
   - **Order**: Display order number (e.g., 1, 2, 3)
   - **Name**: Task name (e.g., "Onboarding Process Brief")
   - **Category**: Optional category (e.g., "Security", "Safety")
   - **Requires Score**: Check if this task has a quiz/test score
   - **Description**: Optional detailed description

Example tasks from your Excel sheet:
- Order 1: Onboarding Process Brief
- Order 2: Police Clearance Form
- Order 3: Document Release Form/NDA
- Order 4: U.S. Citizen / ID Check
- Order 5: Read SOP's 208, 210
- etc.

### 3. Add Trainees
1. In the admin panel, navigate to "Trainees"
2. Click "Add Trainee" and fill in:
   - **Badge Number**: e.g., #2523
   - **First Name**: Trainee's first name
   - **Last Name**: Trainee's last name
   - **Cohort**: e.g., "Fall 2025"
   - **Is Active**: Check to show in active list

## Usage

### For Staff Members

#### Viewing Trainee Progress
1. Log in to the system
2. Main page shows all active trainees with progress bars
3. Click "View Details" to see individual trainee progress

#### Signing Off Tasks
1. Navigate to a trainee's detail page
2. Find the task you want to sign off
3. Click "Sign Off" button
4. Enter score (if applicable) and any notes
5. Click "Confirm Sign Off"
6. The system automatically records your name and timestamp

### For Administrators

#### Managing Data
- Use the admin panel at /admin for all data management
- You can add, edit, or delete trainees, tasks, and sign-offs
- View detailed reports and filter data

## Network Access (Shared Drive)

To make the application accessible across your network:

1. **Find your computer's IP address:**
   ```bash
   # On Windows
   ipconfig

   # On Linux/Mac
   ifconfig
   ```

2. **Run the server on all interfaces:**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

3. **Other users can access via:**
   ```
   http://YOUR_IP_ADDRESS:8000
   ```
   Replace YOUR_IP_ADDRESS with your actual IP (e.g., http://192.168.1.100:8000)

4. **For persistent access:**
   - Consider setting up the server to run as a service
   - Or use a dedicated server machine that stays on
   - Update `ALLOWED_HOSTS` in settings.py for production

## Data Migration from Excel

To import your existing trainee data from Excel:

1. Open the Django shell:
   ```bash
   python manage.py shell
   ```

2. Run import script (you can create a custom management command):
   ```python
   import pandas as pd
   from tracker.models import Trainee, Task

   # Read Excel file
   df = pd.read_excel('Check list Orientation Fall 2025.xlsx')

   # Import trainees (adjust based on your Excel structure)
   for index, row in df.iterrows():
       if pd.notna(row['Badge Number']) and row['Badge Number'] != 'Badge Number':
           Trainee.objects.get_or_create(
               badge_number=row['Badge Number'],
               defaults={
                   'first_name': row['NAME'].split(',')[1].strip() if ',' in str(row['NAME']) else '',
                   'last_name': row['NAME'].split(',')[0].strip() if ',' in str(row['NAME']) else row['NAME'],
                   'cohort': 'Fall 2025'
               }
           )
   ```

## Backup and Maintenance

### Backup Database
The database is stored in `db.sqlite3`. To backup:
```bash
cp db.sqlite3 db.sqlite3.backup
```

### Regular Maintenance
- Regularly backup the database file
- Keep the virtual environment updated
- Monitor disk space if storing on shared drive

## Troubleshooting

### Server won't start
- Check if port 8000 is already in use
- Try a different port: `python manage.py runserver 0.0.0.0:8080`

### Can't access from other computers
- Check firewall settings
- Ensure server is running with 0.0.0.0 (not 127.0.0.1)
- Verify network connectivity

### Forgot admin password
```bash
python manage.py changepassword admin_username
```

## Support

For issues or questions:
1. Check the Django documentation: https://docs.djangoproject.com/
2. Review the code comments in the project files
3. Contact your system administrator

## Security Notes

**Important for Production Use:**
1. Change `SECRET_KEY` in settings.py
2. Set `DEBUG = False` in settings.py
3. Update `ALLOWED_HOSTS` with specific domains/IPs
4. Use HTTPS for secure connections
5. Regularly update Django and dependencies
6. Use strong passwords for all accounts
