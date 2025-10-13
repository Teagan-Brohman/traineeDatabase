# Release Guide

This guide explains how to publish updates to the Trainee Badge Tracker application.

## Version Numbering

Use [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes (e.g., database structure changes requiring data migration)
- **MINOR**: New features, backwards-compatible (e.g., new reports, bulk operations)
- **PATCH**: Bug fixes, small improvements (e.g., UI fixes, performance improvements)

Examples:
- `1.0.0` → `1.0.1`: Bug fix (logout button fixed)
- `1.0.1` → `1.1.0`: New feature (bulk sign-off added)
- `1.1.0` → `2.0.0`: Breaking change (new database schema)

## Pre-Release Checklist

Before publishing a new version:

- [ ] All tests pass: `python manage.py test`
- [ ] Database migrations created: `python manage.py makemigrations`
- [ ] Update `version.txt` with new version number
- [ ] Update `DEPLOYMENT_README.txt` version history section
- [ ] Test fresh install with `FIRST_TIME_SETUP.bat`
- [ ] Test update with `UPDATE_FROM_GITHUB.bat`
- [ ] Review changes in `git status` and `git diff`

## Release Process

### Method 1: GitHub Releases (Recommended)

#### Step 1: Commit and Push Changes

```bash
# Check what's changed
git status
git diff

# Stage changes
git add .

# Commit with descriptive message
git commit -m "Release v1.1.0: Add bulk sign-off feature

- Add bulk sign-off functionality
- Fix logout button redirect
- Update documentation
- Add 10 new tests"

# Push to GitHub
git push origin main
```

#### Step 2: Create GitHub Release

1. Go to: https://github.com/Teagan-Brohman/traineeDatabase/releases
2. Click "Create a new release"
3. Tag: `v1.1.0` (match version.txt)
4. Release title: `Version 1.1.0 - Bulk Sign-Off Feature`
5. Description:
   ```markdown
   ## What's New
   - ✨ Bulk sign-off feature for multiple trainees
   - 🐛 Fixed logout button redirect
   - 📝 Updated documentation

   ## Installation
   - New users: Download `traineeDatabase_DEPLOYMENT.zip`
   - Existing users: Run `UPDATE_FROM_GITHUB.bat` or download update ZIP

   ## Breaking Changes
   None

   ## Full Changelog
   https://github.com/Teagan-Brohman/traineeDatabase/compare/v1.0.0...v1.1.0
   ```
6. Attach files:
   - `traineeDatabase_DEPLOYMENT.zip` (full deployment package)
   - `traineeDatabase_UPDATE.zip` (update-only package, see below)
7. Click "Publish release"

#### Step 3: Create Update-Only ZIP

For users who want to update without downloading the full 107 MB package:

```bash
# From project root
# Create a zip with ONLY the code/docs, exclude wheels and portable_python

# Windows PowerShell:
Compress-Archive -Path tracker,trainee_tracker,*.py,*.bat,*.txt,*.md,requirements*.txt,.env.example -DestinationPath traineeDatabase_UPDATE.zip

# OR manually:
# - Create new zip file
# - Add: tracker/ folder
# - Add: trainee_tracker/ folder
# - Add: *.py files
# - Add: *.bat files
# - Add: *.txt and *.md files
# - Add: requirements.txt and requirements-postgres.txt
# - Add: .env.example
# - DO NOT add: wheels/, venv/, db.sqlite3, .env, logs/
```

Upload `traineeDatabase_UPDATE.zip` (~5-10 MB) to the GitHub release.

### Method 2: Direct Push (Quick Updates)

For minor bug fixes that don't need a formal release:

```bash
# Make changes
# Test changes

# Commit and push
git add .
git commit -m "Fix: Correct cohort ordering in admin"
git push origin main

# Update version.txt (patch version)
# Users can pull with UPDATE_FROM_GITHUB.bat
```

## Post-Release

### Notify Users

Create an announcement (email, Teams, etc.):

```
Subject: Trainee Tracker Update Available - Version 1.1.0

A new version of the Trainee Badge Tracker is now available!

What's New:
- Bulk sign-off feature
- Fixed logout button
- Updated documentation

How to Update:
1. Option A (with Git):
   - Run UPDATE_FROM_GITHUB.bat

2. Option B (without Git):
   - Download traineeDatabase_UPDATE.zip from:
     https://github.com/Teagan-Brohman/traineeDatabase/releases/latest
   - Run UPDATE_FROM_ZIP.bat
   - Point to the downloaded ZIP

Your database and settings will be automatically preserved.
A backup will be created before updating.

Questions? See HOW_TO_USE.txt or contact [your contact info]
```

### Monitor for Issues

- Check GitHub Issues: https://github.com/Teagan-Brohman/traineeDatabase/issues
- Be available for user questions
- Prepare hotfix if critical bugs are found

## Hotfix Process

For critical bugs that need immediate fixing:

```bash
# Fix the bug
# Test thoroughly

# Update version (patch increment)
echo 1.1.1 > version.txt

# Commit and push
git add .
git commit -m "Hotfix v1.1.1: Fix critical database migration error"
git push origin main

# Create GitHub release (mark as "pre-release" if unstable)
# Notify users immediately
```

## Rollback Process

If an update causes problems:

```bash
# Revert to previous version
git revert HEAD
git push origin main

# OR reset to specific version
git reset --hard v1.0.0
git push origin main --force  # Use with caution!

# Notify users to restore from backup:
# - Copy db.sqlite3 from backups/backup_YYYYMMDD_HHMMSS/
# - Copy .env if needed
```

## Changelog Maintenance

Keep a CHANGELOG.md file (create if doesn't exist):

```markdown
# Changelog

## [1.1.0] - 2025-10-10

### Added
- Bulk sign-off feature for multiple trainees
- Export to CSV functionality

### Fixed
- Logout button now redirects correctly
- Cohort ordering in admin panel

### Changed
- Updated dependencies to latest versions
- Improved performance of trainee list view

## [1.0.0] - 2025-10-01

### Added
- Initial release
- Complete trainee tracking system
- 15 training tasks
- Excel import/export
- Offline installation support
```

## Testing Checklist

Before each release, test these scenarios:

### Fresh Installation
- [ ] Extract deployment ZIP
- [ ] Run FIRST_TIME_SETUP.bat
- [ ] Create admin user
- [ ] Run START_SERVER.bat
- [ ] Access http://localhost:8000
- [ ] Login and test basic functionality

### Update from Previous Version
- [ ] Start with v1.0.0 installed
- [ ] Run UPDATE_FROM_GITHUB.bat
- [ ] Verify database intact
- [ ] Verify settings preserved
- [ ] Test new features
- [ ] Test existing features still work

### Offline Installation
- [ ] Disconnect from internet
- [ ] Run FIRST_TIME_SETUP.bat
- [ ] Verify wheels are used
- [ ] Verify installation succeeds

### Network Deployment
- [ ] Start server on one computer
- [ ] Access from another computer
- [ ] Test sign-off functionality
- [ ] Test concurrent access

## Common Issues

### "Git not found" during update
- Users need to install Git OR use UPDATE_FROM_ZIP.bat instead
- Provide download link: https://git-scm.com/download/win

### "Authentication failed" when pushing
- Need to set up GitHub credentials
- Use GitHub Personal Access Token
- OR use GitHub Desktop app

### Merge conflicts during update
- User has local changes
- Solution: Backup changes, reset repo, reapply changes

### Database migration fails
- Breaking change in models
- Provide data migration script
- Document manual steps if needed

## Resources

- GitHub Repository: https://github.com/Teagan-Brohman/traineeDatabase
- Django Migrations: https://docs.djangoproject.com/en/stable/topics/migrations/
- Semantic Versioning: https://semver.org/
- Git Basics: https://git-scm.com/book/en/v2

## Questions?

For release process questions, refer to this guide or check Django documentation.

---

**Last Updated:** 2025-10-13
**Maintainer:** [Your Name]
