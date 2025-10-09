# Quick Start Guide

## 🚀 EASIEST WAY TO START (Network Drive - No Technical Knowledge Required)

**If you're running this from a shared network drive and want the simplest setup:**

1. **Double-click**: `FIRST_TIME_SETUP.bat` (only do this once)
2. **Double-click**: `START_SERVER.bat` (do this each time you want to use the app)
3. **Open browser**: Go to the address shown in the window
4. **Read**: `HOW_TO_USE.txt` for detailed non-technical instructions

That's it! See HOW_TO_USE.txt for complete beginner-friendly instructions.

---

## Advanced Setup (For Technical Users)

### Your system is ready to use! 🎉

### What's Been Set Up

✅ Django web application installed and configured
✅ Database created with all necessary tables
✅ 15 training tasks imported from your Excel file
✅ 66 trainees imported (Fall 2025 cohort)
✅ User-friendly web interface created
✅ Admin panel configured for management

### Next Steps

#### 1. Create an Admin Account (REQUIRED - Do this first!)

```bash
# Activate virtual environment
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate     # On Windows

# Create superuser
python manage.py createsuperuser
```

Follow the prompts to create your admin username and password.

#### 2. Start the Server

```bash
# For local access only:
python manage.py runserver

# For network/shared drive access:
python manage.py runserver 0.0.0.0:8000
```

#### 3. Access the Application

Open your web browser and go to:
- **Main Interface**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin

#### 4. Create Staff Accounts

1. Log in to the admin panel
2. Go to **Users** → **Add User**
3. Create accounts for each staff member who will sign off tasks
4. After creating each user:
   - Edit the user
   - Scroll down to "Staff Profile" section
   - Enter their initials (e.g., "JD" for John Doe)
   - Save

#### 5. Start Using the System

**For Staff Members:**
1. Log in at http://localhost:8000
2. You'll see the list of all trainees with progress bars
3. Click "View Details" on any trainee
4. Click "Sign Off" next to completed tasks
5. Enter score (if quiz) and any notes
6. Submit

**For Administrators:**
- Use the admin panel at http://localhost:8000/admin
- Manage trainees, tasks, staff, and sign-offs
- Export data and run reports

### Network Access (For Shared Drive Use)

To allow other computers to access the system:

1. Find your computer's IP address:
   ```bash
   ipconfig          # Windows
   ifconfig          # Linux/Mac
   ip addr show      # Linux alternative
   ```

2. Start server for network access:
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

3. Share this URL with your team:
   ```
   http://YOUR_IP_ADDRESS:8000
   ```
   Example: `http://192.168.1.100:8000`

### Imported Data

**Tasks (15 total):**
1. Onboarding Process Brief
2. Police Clearance Form
3. Document Release Form/NDA
4. U.S. Citizen / ID Check
5. Read SOP's 208, 210
6. Read SOP 501 A&B
7. Read SOP's 505, 506, 508, 509, 510
8. Read SOP's 600, 601
9. Onboarding Tour
10. Onboarding Tour Quiz (requires score)
11. Read R.G. 8.13, R.G. 8.29
12. ALARA Statement
13. Radiation Safety PowerPoint & Video
14. Reg Guides 8.13 / 8.29 Quiz (requires score)
15. Review Deficiencies

**Trainees:** 66 trainees from Fall 2025 cohort (badge #2523 - #2594)

### Tips

- **Backup regularly**: Copy `db.sqlite3` to a safe location
- **Keep server running**: For continuous access, run server on a dedicated machine
- **Use strong passwords**: Especially for admin accounts
- **Check firewall**: Make sure port 8000 is allowed for network access

### Troubleshooting

**Can't access from other computers?**
- Make sure you started with `0.0.0.0:8000` not `127.0.0.1:8000`
- Check your firewall settings
- Verify the IP address is correct

**Forgot admin password?**
```bash
python manage.py changepassword your_username
```

**Need to add more trainees?**
- Use the admin panel, or
- Edit `import_data.py` and run it again

### Support Files

- `README.md` - Full documentation
- `import_data.py` - Script to import data from Excel
- `requirements.txt` - Python dependencies
- `db.sqlite3` - Your database (backup this file!)

---

**You're all set! Start by creating your admin account, then log in and explore the system.**
