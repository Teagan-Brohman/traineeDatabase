# PostgreSQL Configuration Guide

This document provides instructions for migrating from SQLite to PostgreSQL for production deployments.

## Why PostgreSQL?

While SQLite is excellent for development and small deployments, PostgreSQL is recommended for production because:

- **Better concurrency**: Handles multiple simultaneous write operations
- **Network deployment**: Multiple users can access the database simultaneously without file locking issues
- **Data integrity**: Better ACID compliance and transaction handling
- **Scalability**: Can handle larger datasets and more complex queries efficiently
- **Advanced features**: Full-text search, JSON support, and more robust backup/restore

## Prerequisites

1. **Install PostgreSQL** on your server or local machine
   - Windows: Download from https://www.postgresql.org/download/windows/
   - Linux: `sudo apt-get install postgresql postgresql-contrib` (Ubuntu/Debian)
   - macOS: `brew install postgresql`

2. **Install Python PostgreSQL adapter**
   ```bash
   pip install psycopg2-binary
   ```

## Step-by-Step Setup

### 1. Create PostgreSQL Database

```bash
# Login to PostgreSQL as superuser
sudo -u postgres psql

# Create database
CREATE DATABASE trainee_tracker;

# Create user with password
CREATE USER tracker_user WITH PASSWORD 'your_secure_password_here';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE trainee_tracker TO tracker_user;

# In PostgreSQL 15+, also grant schema permissions
\c trainee_tracker
GRANT ALL ON SCHEMA public TO tracker_user;

# Exit psql
\q
```

### 2. Install PostgreSQL Python Adapter

The base `requirements.txt` includes only SQLite dependencies. For PostgreSQL, install additional requirements:

```bash
# After installing base requirements
pip install -r requirements-postgres.txt
```

**Windows Users:** If you encounter build errors (`vswhere.exe` not found), see options in `requirements-postgres.txt`.

Alternatively, install manually:
```bash
pip install psycopg2-binary==2.9.9
```

### 3. Configure Environment Variables

Update your `.env` file with PostgreSQL settings:

```bash
# Database Configuration
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=trainee_tracker
DATABASE_USER=tracker_user
DATABASE_PASSWORD=your_secure_password_here
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

### 4. Test Database Connection

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Test Django can connect
python manage.py check --database default
```

### 5. Migrate Database Schema

```bash
# Run migrations to create tables
python manage.py migrate

# Create superuser account
python manage.py createsuperuser
```

### 6. Import Existing Data (Optional)

If migrating from existing SQLite database:

```bash
# Export data from SQLite
python manage.py dumpdata --natural-foreign --natural-primary \
    --exclude auth.permission --exclude contenttypes \
    -o data_backup.json

# Update .env to use PostgreSQL settings

# Import data to PostgreSQL
python manage.py loaddata data_backup.json
```

## Production Deployment Settings

For production deployment, ensure these settings in your `.env`:

```bash
# Django Settings
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,server-ip-address

# Security Settings (HTTPS only)
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

## PostgreSQL Performance Tuning

### Connection Pooling

For high-traffic scenarios, consider using connection pooling:

```python
# In settings.py, add:
DATABASES['default']['CONN_MAX_AGE'] = 600  # 10 minutes
```

### Database Indexes

The application already includes optimized indexes for:
- Trainee lookups (badge_number, name, cohort)
- Task ordering and categorization
- SignOff queries by trainee and date
- Archive searches

### Backup Strategy

```bash
# Create backup
pg_dump -U tracker_user -h localhost trainee_tracker > backup_$(date +%Y%m%d).sql

# Restore backup
psql -U tracker_user -h localhost trainee_tracker < backup_20250101.sql
```

## Automated Backups (Linux/macOS)

Create a backup script `backup_db.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/path/to/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="trainee_tracker"
DB_USER="tracker_user"

# Create backup
pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_DIR/backup_$TIMESTAMP.sql.gz

# Keep only last 30 days of backups
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete
```

Add to crontab for daily backups at 2 AM:
```bash
0 2 * * * /path/to/backup_db.sh
```

## Monitoring and Maintenance

### Check Database Size

```sql
SELECT pg_size_pretty(pg_database_size('trainee_tracker'));
```

### View Active Connections

```sql
SELECT count(*) FROM pg_stat_activity
WHERE datname = 'trainee_tracker';
```

### Vacuum Database (Maintenance)

```bash
# Run weekly to optimize performance
python manage.py dbshell
VACUUM ANALYZE;
\q
```

## Troubleshooting

### Connection Refused Error

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list  # macOS

# Start if not running
sudo systemctl start postgresql  # Linux
brew services start postgresql  # macOS
```

### Authentication Failed

1. Check `pg_hba.conf` allows password authentication
2. Verify user password is correct
3. Ensure database and user exist

```bash
sudo -u postgres psql -c "\du"  # List users
sudo -u postgres psql -c "\l"   # List databases
```

### Permission Denied Errors

```sql
-- Grant all necessary permissions
GRANT ALL PRIVILEGES ON DATABASE trainee_tracker TO tracker_user;
GRANT ALL ON SCHEMA public TO tracker_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO tracker_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO tracker_user;
```

## Reverting to SQLite

If you need to switch back to SQLite, update `.env`:

```bash
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=db.sqlite3
```

Then run migrations:
```bash
python manage.py migrate
```

## Additional Resources

- [Django PostgreSQL Documentation](https://docs.djangoproject.com/en/stable/ref/databases/#postgresql-notes)
- [PostgreSQL Official Docs](https://www.postgresql.org/docs/)
- [psycopg2 Documentation](https://www.psycopg.org/docs/)
