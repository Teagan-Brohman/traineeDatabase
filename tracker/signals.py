"""
Django signals for bi-directional synchronization between Trainee and AdvancedStaff models.

This module implements automatic synchronization when records are created or updated:
- Creating/updating a Trainee automatically creates/updates corresponding AdvancedStaff
- Creating/updating an AdvancedStaff automatically creates/updates corresponding Trainee

Uses thread-local context managers to prevent infinite signal loops.
"""

import threading
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Trainee, AdvancedStaff, Cohort


# Thread-local storage for sync context
_sync_context = threading.local()


class SyncContext:
    """
    Context manager to prevent infinite signal loops using thread-local storage.

    When syncing from Trainee → AdvancedStaff, this prevents the AdvancedStaff
    post_save signal from syncing back to Trainee, which would create an infinite loop.
    """

    def __init__(self, model_name):
        self.model_name = model_name

    def __enter__(self):
        if not hasattr(_sync_context, 'active_syncs'):
            _sync_context.active_syncs = set()
        _sync_context.active_syncs.add(self.model_name)
        return self

    def __exit__(self, *args):
        _sync_context.active_syncs.discard(self.model_name)

    @staticmethod
    def is_syncing(model_name):
        """Check if we're currently syncing the specified model."""
        if not hasattr(_sync_context, 'active_syncs'):
            return False
        return model_name in _sync_context.active_syncs


# Global flag to disable sync (useful for mass imports)
# Set to True initially for safe deployment
DISABLE_SYNC = True


@receiver(post_save, sender=Trainee)
def sync_trainee_to_advanced(sender, instance, created, **kwargs):
    """
    Auto-sync Trainee → AdvancedStaff.

    When a Trainee is created or updated, this signal:
    1. Finds the corresponding AdvancedStaff (by badge number)
    2. Updates fields (first_name, last_name, is_active) if they differ
    3. Creates new AdvancedStaff if one doesn't exist

    Badge number normalization: Trainee "#2523" → AdvancedStaff "2523"
    """
    global DISABLE_SYNC

    # Skip if sync is disabled globally
    if DISABLE_SYNC:
        return

    # Skip if currently syncing AdvancedStaff (prevent infinite loop)
    if SyncContext.is_syncing('AdvancedStaff'):
        return

    # Skip bulk operations (raw saves from loaddata, etc.)
    if kwargs.get('raw', False):
        return

    with SyncContext('Trainee'):
        # Normalize badge: strip # from Trainee's "#2523" → "2523"
        normalized_badge = instance.badge_number.lstrip('#')

        try:
            # Find existing AdvancedStaff
            adv_staff = AdvancedStaff.objects.get(badge_number=normalized_badge)

            # Only update if fields actually differ (avoid unnecessary writes)
            if (adv_staff.first_name != instance.first_name or
                adv_staff.last_name != instance.last_name or
                adv_staff.is_active != instance.is_active):

                adv_staff.first_name = instance.first_name
                adv_staff.last_name = instance.last_name
                adv_staff.is_active = instance.is_active
                adv_staff.save(update_fields=['first_name', 'last_name', 'is_active'])

        except AdvancedStaff.DoesNotExist:
            # Create new AdvancedStaff record
            AdvancedStaff.objects.create(
                badge_number=normalized_badge,
                first_name=instance.first_name,
                last_name=instance.last_name,
                role='Trainee',  # Default role for new staff from orientation
                badge_status='badging_in_progress',  # Default status
                is_active=instance.is_active
            )


@receiver(post_save, sender=AdvancedStaff)
def sync_advanced_to_trainee(sender, instance, created, **kwargs):
    """
    Auto-sync AdvancedStaff → Trainee.

    When an AdvancedStaff is created or updated, this signal:
    1. Finds the corresponding Trainee (by badge number)
    2. Updates fields (first_name, last_name, is_active) if they differ
    3. Creates new Trainee if one doesn't exist (assigned to current cohort)

    Badge number normalization: AdvancedStaff "2523" → Trainee "#2523"
    """
    global DISABLE_SYNC

    # Skip if sync is disabled globally
    if DISABLE_SYNC:
        return

    # Skip if currently syncing Trainee (prevent infinite loop)
    if SyncContext.is_syncing('Trainee'):
        return

    # Skip bulk operations
    if kwargs.get('raw', False):
        return

    with SyncContext('AdvancedStaff'):
        # Normalize badge: add # to AdvancedStaff's "2523" → "#2523"
        normalized_badge = f"#{instance.badge_number.lstrip('#')}"

        try:
            # Find existing Trainee
            trainee = Trainee.objects.get(badge_number=normalized_badge)

            # Only update if fields actually differ
            if (trainee.first_name != instance.first_name or
                trainee.last_name != instance.last_name or
                trainee.is_active != instance.is_active):

                trainee.first_name = instance.first_name
                trainee.last_name = instance.last_name
                trainee.is_active = instance.is_active
                trainee.save(update_fields=['first_name', 'last_name', 'is_active'])

        except Trainee.DoesNotExist:
            # Create new Trainee record with current cohort
            current_cohort = Cohort.get_current_cohort()
            if current_cohort:
                Trainee.objects.create(
                    badge_number=normalized_badge,
                    first_name=instance.first_name,
                    last_name=instance.last_name,
                    cohort=current_cohort,
                    is_active=instance.is_active
                )
