"""
Trainee Tracker - Activity Tracking Middleware
========================================
This middleware tracks the last HTTP request time to enable
idle timeout monitoring.

TEMPORARY SOLUTION: This is part of the SQLite network drive safeguards.
Remove this when migrating to PostgreSQL.
========================================
"""

from datetime import datetime
from pathlib import Path


class ActivityTrackerMiddleware:
    """
    Middleware to track last activity time.

    Updates LAST_ACTIVITY.txt file with timestamp of every HTTP request.
    This file is monitored by idle_monitor.py to determine if the server
    should shut down due to inactivity.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.activity_file = Path(__file__).resolve().parent.parent / 'LAST_ACTIVITY.txt'

    def __call__(self, request):
        # Update activity timestamp before processing request
        self.update_activity()

        # Process the request
        response = self.get_response(request)

        return response

    def update_activity(self):
        """Write current timestamp to activity file."""
        try:
            timestamp = datetime.now().isoformat()
            with open(self.activity_file, 'w') as f:
                f.write(timestamp)
        except Exception:
            # Silently fail - don't break requests if activity tracking fails
            pass
