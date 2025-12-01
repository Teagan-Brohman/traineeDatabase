"""
Utility functions for the tracker app.
"""


def normalize_badge_for_trainee(badge_number):
    """
    Normalize badge number to Trainee format (WITH #).

    Args:
        badge_number: Badge number as string (e.g., "#2523" or "2523")

    Returns:
        Badge number with # prefix (e.g., "#2523")

    Examples:
        >>> normalize_badge_for_trainee("2523")
        "#2523"
        >>> normalize_badge_for_trainee("#2523")
        "#2523"
    """
    if not badge_number:
        return badge_number
    badge = str(badge_number).strip()
    if not badge.startswith('#'):
        badge = f"#{badge}"
    return badge


def normalize_badge_for_advanced(badge_number):
    """
    Normalize badge number to AdvancedStaff format (WITHOUT #).

    Args:
        badge_number: Badge number as string (e.g., "#2523" or "2523")

    Returns:
        Badge number without # prefix (e.g., "2523")

    Examples:
        >>> normalize_badge_for_advanced("#2523")
        "2523"
        >>> normalize_badge_for_advanced("2523")
        "2523"
    """
    if not badge_number:
        return badge_number
    return str(badge_number).strip().lstrip('#')


def find_trainee_by_badge(badge_number):
    """
    Find Trainee by badge number, handling normalization.

    Args:
        badge_number: Badge number in any format

    Returns:
        Trainee instance or None if not found
    """
    from .models import Trainee
    normalized = normalize_badge_for_trainee(badge_number)
    try:
        return Trainee.objects.get(badge_number=normalized)
    except Trainee.DoesNotExist:
        return None


def find_advanced_staff_by_badge(badge_number):
    """
    Find AdvancedStaff by badge number, handling normalization.

    Args:
        badge_number: Badge number in any format

    Returns:
        AdvancedStaff instance or None if not found
    """
    from .models import AdvancedStaff
    normalized = normalize_badge_for_advanced(badge_number)
    try:
        return AdvancedStaff.objects.get(badge_number=normalized)
    except AdvancedStaff.DoesNotExist:
        return None
