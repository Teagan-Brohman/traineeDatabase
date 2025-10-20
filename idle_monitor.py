#!/usr/bin/env python
"""
Trainee Tracker - Idle Monitor
========================================
This script monitors server activity and shuts down the Django server
after a configurable period of inactivity.

Configuration:
- IDLE_TIMEOUT_MINUTES: Minutes of inactivity before shutdown (default: 120 = 2 hours)
- CHECK_INTERVAL_SECONDS: How often to check for activity (default: 300 = 5 minutes)

The script reads LAST_ACTIVITY timestamp written by Django middleware.
If no requests have been made within the timeout period, it gracefully
shuts down the server.

NOTE: This is a TEMPORARY solution for SQLite on network drive.
      Remove this when migrating to PostgreSQL.
========================================
"""

import os
import sys
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
IDLE_TIMEOUT_MINUTES = int(os.environ.get('IDLE_TIMEOUT_MINUTES', '120'))  # 2 hours default
CHECK_INTERVAL_SECONDS = int(os.environ.get('CHECK_INTERVAL_SECONDS', '300'))  # 5 minutes default
ACTIVITY_FILE = 'LAST_ACTIVITY.txt'
LOCK_FILE = 'SERVER_LOCK'

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('idle_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def get_last_activity():
    """Read the last activity timestamp from file."""
    try:
        if os.path.exists(ACTIVITY_FILE):
            with open(ACTIVITY_FILE, 'r') as f:
                timestamp_str = f.read().strip()
                return datetime.fromisoformat(timestamp_str)
        else:
            # File doesn't exist yet - server just started
            return datetime.now()
    except Exception as e:
        logger.error(f"Error reading activity file: {e}")
        return datetime.now()


def check_lock_file_exists():
    """Check if server lock file still exists."""
    return os.path.exists(LOCK_FILE)


def shutdown_server():
    """Gracefully shutdown the Django server."""
    logger.warning(f"Shutting down server due to {IDLE_TIMEOUT_MINUTES} minutes of inactivity")

    # Clean up lock file
    try:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
            logger.info("Removed server lock file")
    except Exception as e:
        logger.error(f"Error removing lock file: {e}")

    # Find and kill the Django server process
    import platform
    if platform.system() == 'Windows':
        # Find Python process running manage.py runserver
        os.system('taskkill /F /FI "WINDOWTITLE eq Trainee*" /T >nul 2>&1')
        os.system('taskkill /F /IM python.exe /FI "COMMANDLINE eq *runserver*" >nul 2>&1')
    else:
        # Unix-like systems
        os.system('pkill -f "manage.py runserver"')

    logger.info("Server shutdown complete")
    sys.exit(0)


def main():
    """Main monitoring loop."""
    logger.info("="*60)
    logger.info("Idle Monitor Started")
    logger.info(f"Idle timeout: {IDLE_TIMEOUT_MINUTES} minutes")
    logger.info(f"Check interval: {CHECK_INTERVAL_SECONDS} seconds")
    logger.info("="*60)

    check_count = 0

    while True:
        try:
            # Check if lock file still exists (server might have been stopped manually)
            if not check_lock_file_exists():
                logger.info("Lock file removed - server stopped externally. Exiting monitor...")
                sys.exit(0)

            # Get last activity time
            last_activity = get_last_activity()
            now = datetime.now()
            idle_duration = now - last_activity
            idle_minutes = idle_duration.total_seconds() / 60

            check_count += 1

            # Log status
            if idle_minutes < 1:
                status = "ACTIVE"
                logger.info(f"Check #{check_count}: {status} - Last activity: {idle_duration.seconds} seconds ago")
            else:
                remaining_minutes = IDLE_TIMEOUT_MINUTES - idle_minutes
                if remaining_minutes > 0:
                    status = "IDLE"
                    logger.info(
                        f"Check #{check_count}: {status} - "
                        f"Idle for {int(idle_minutes)} minutes, "
                        f"shutdown in {int(remaining_minutes)} minutes"
                    )
                else:
                    # Timeout exceeded - shutdown
                    logger.warning(f"Idle timeout exceeded ({int(idle_minutes)} minutes)")
                    shutdown_server()

            # Sleep until next check
            time.sleep(CHECK_INTERVAL_SECONDS)

        except KeyboardInterrupt:
            logger.info("Idle monitor stopped by user")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
            time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == '__main__':
    main()
