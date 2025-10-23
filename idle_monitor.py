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
IDLE_TIMEOUT_MINUTES = int(os.environ.get('IDLE_TIMEOUT_MINUTES', '20'))  # 20 minutes default
CHECK_INTERVAL_SECONDS = int(os.environ.get('CHECK_INTERVAL_SECONDS', '300'))  # 5 minutes default
FAST_CHECK_INTERVAL = 3  # Check every 3 seconds if Django server is still running
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


def initialize_activity_file():
    """Initialize the activity file with current timestamp.

    This prevents the idle monitor from reading stale timestamps
    from previous server runs that would cause immediate shutdown.
    """
    try:
        timestamp = datetime.now().isoformat()
        with open(ACTIVITY_FILE, 'w') as f:
            f.write(timestamp)
        logger.info(f"Initialized activity tracking (start time: {timestamp})")
    except Exception as e:
        logger.error(f"Error initializing activity file: {e}")


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


def check_django_running():
    """Check if Django server is still running on port 8000.

    Returns True if the Django server is running (port 8000 is in use),
    False otherwise. This allows detection of forceful window closure.
    """
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Try to connect to port 8000
        result = sock.connect_ex(('127.0.0.1', 8000))
        sock.close()
        return result == 0  # 0 means connection successful (port in use)
    except Exception as e:
        logger.debug(f"Error checking Django server status: {e}")
        return False


def cleanup_and_exit(reason="Unknown"):
    """Clean up lock file and exit gracefully.

    Args:
        reason: String describing why we're exiting
    """
    logger.info(f"Exiting idle monitor: {reason}")

    # Clean up lock file
    try:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
            logger.info("Removed server lock file")
    except Exception as e:
        logger.error(f"Error removing lock file: {e}")

    logger.info("Idle monitor shutdown complete")
    sys.exit(0)


def shutdown_server():
    """Gracefully shutdown the Django server due to idle timeout."""
    logger.warning(f"Shutting down server due to {IDLE_TIMEOUT_MINUTES} minutes of inactivity")

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
    cleanup_and_exit("Idle timeout exceeded")


def wait_for_django_startup():
    """Wait for Django server to start up before monitoring.

    Django takes time to start (loading modules, migrations, etc.),
    so we need to wait until it's actually running before we start
    checking if it goes down.
    """
    logger.info("Waiting for Django server to start...")
    max_wait_time = 60  # Wait up to 60 seconds
    check_interval = 2  # Check every 2 seconds

    for attempt in range(max_wait_time // check_interval):
        if check_django_running():
            logger.info(f"Django server detected on port 8000 (after {attempt * check_interval} seconds)")
            return True
        time.sleep(check_interval)

    # Django didn't start within timeout
    logger.warning(f"Django server not detected after {max_wait_time} seconds")
    logger.warning("Continuing anyway - server may still be starting...")
    return False


def main():
    """Main monitoring loop with two-tier checking.

    Fast checks (every 3 seconds):
        - Server lock file exists
        - Django server still running on port 8000

    Slow checks (every 5 minutes):
        - Idle timeout monitoring
    """
    logger.info("="*60)
    logger.info("Idle Monitor Started")
    logger.info(f"Idle timeout: {IDLE_TIMEOUT_MINUTES} minutes")
    logger.info(f"Idle check interval: {CHECK_INTERVAL_SECONDS} seconds")
    logger.info(f"Fast check interval: {FAST_CHECK_INTERVAL} seconds")
    logger.info("="*60)

    # Initialize activity file with current timestamp to prevent
    # stale timestamps from previous runs causing immediate shutdown
    initialize_activity_file()

    # Wait for Django to start before beginning monitoring
    # This prevents false "server not running" detection during startup
    django_started = wait_for_django_startup()

    # Calculate how many fast checks = one idle check
    fast_checks_per_idle_check = CHECK_INTERVAL_SECONDS // FAST_CHECK_INTERVAL

    fast_check_count = 0
    idle_check_count = 0

    while True:
        try:
            fast_check_count += 1

            # ========================================
            # FAST CHECKS (every 3 seconds)
            # ========================================

            # Check if lock file still exists
            if not check_lock_file_exists():
                cleanup_and_exit("Lock file removed - server stopped externally")

            # Check if Django server is still running (only if it started successfully)
            if django_started and not check_django_running():
                cleanup_and_exit("Django server no longer running - window likely closed")

            # ========================================
            # SLOW CHECKS (every 5 minutes)
            # ========================================

            if fast_check_count >= fast_checks_per_idle_check:
                # Reset fast check counter
                fast_check_count = 0
                idle_check_count += 1

                # Get last activity time
                last_activity = get_last_activity()
                now = datetime.now()
                idle_duration = now - last_activity
                idle_minutes = idle_duration.total_seconds() / 60

                # Log status
                if idle_minutes < 1:
                    status = "ACTIVE"
                    logger.info(f"Check #{idle_check_count}: {status} - Last activity: {idle_duration.seconds} seconds ago")
                else:
                    remaining_minutes = IDLE_TIMEOUT_MINUTES - idle_minutes
                    if remaining_minutes > 0:
                        status = "IDLE"
                        logger.info(
                            f"Check #{idle_check_count}: {status} - "
                            f"Idle for {int(idle_minutes)} minutes, "
                            f"shutdown in {int(remaining_minutes)} minutes"
                        )
                    else:
                        # Timeout exceeded - shutdown
                        logger.warning(f"Idle timeout exceeded ({int(idle_minutes)} minutes)")
                        shutdown_server()

            # Sleep until next fast check
            time.sleep(FAST_CHECK_INTERVAL)

        except KeyboardInterrupt:
            cleanup_and_exit("Stopped by user (Ctrl+C)")
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
            time.sleep(FAST_CHECK_INTERVAL)


if __name__ == '__main__':
    main()
