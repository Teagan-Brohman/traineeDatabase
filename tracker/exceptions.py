"""
Custom exceptions for the tracker app business logic.

These exceptions provide better error handling and clearer messaging
for domain-specific error conditions.
"""


class TrackerException(Exception):
    """Base exception for all tracker-related errors"""
    pass


class AuthorizationError(TrackerException):
    """Raised when a user lacks permission for an operation"""
    pass


class ValidationError(TrackerException):
    """Raised when data validation fails"""
    pass


class ScoreValidationError(ValidationError):
    """Raised when a score does not meet minimum requirements"""

    def __init__(self, score, minimum_score, task_name):
        self.score = score
        self.minimum_score = minimum_score
        self.task_name = task_name
        message = f"Score {score} does not meet the minimum requirement of {minimum_score} for '{task_name}'"
        super().__init__(message)


class MissingScoreError(ValidationError):
    """Raised when a score is required but not provided"""

    def __init__(self, task_name, minimum_score):
        self.task_name = task_name
        self.minimum_score = minimum_score
        message = f"Score is required for '{task_name}'. Minimum passing score: {minimum_score}"
        super().__init__(message)


class InvalidScoreFormatError(ValidationError):
    """Raised when a score is not in a valid numeric format"""

    def __init__(self, score_value):
        self.score_value = score_value
        message = f"Invalid score format: '{score_value}'. Please enter a numeric value."
        super().__init__(message)


class UnauthorizedSignOffError(AuthorizationError):
    """Raised when a user attempts to sign off a task they're not authorized for"""

    def __init__(self, user, task_name):
        self.user = user
        self.task_name = task_name
        message = f"User {user.username} is not authorized to sign off '{task_name}'"
        super().__init__(message)


class SignOffNotFoundError(TrackerException):
    """Raised when attempting to modify a sign-off that doesn't exist"""

    def __init__(self, trainee, task):
        self.trainee = trainee
        self.task = task
        message = f"No sign-off found for {trainee.badge_number} on task '{task.name}'"
        super().__init__(message)


class DuplicateSignOffError(TrackerException):
    """Raised when attempting to create a duplicate sign-off"""

    def __init__(self, trainee, task):
        self.trainee = trainee
        self.task = task
        message = f"Sign-off already exists for {trainee.badge_number} on task '{task.name}'"
        super().__init__(message)


class TaskOrderConflictError(TrackerException):
    """Raised when there's a conflict with task ordering"""

    def __init__(self, order, existing_task):
        self.order = order
        self.existing_task = existing_task
        message = f"Task order {order} is already assigned to '{existing_task.name}'"
        super().__init__(message)


class InactiveCohortError(TrackerException):
    """Raised when attempting operations on an inactive cohort"""

    def __init__(self, cohort):
        self.cohort = cohort
        message = f"Cohort '{cohort.name}' is not currently active"
        super().__init__(message)


class CohortNotFoundError(TrackerException):
    """Raised when no current cohort can be determined"""

    def __init__(self):
        message = "No current cohort found. Please set a cohort as current in the admin panel."
        super().__init__(message)


class BadgeNumberFormatError(ValidationError):
    """Raised when badge number doesn't match expected format"""

    def __init__(self, badge_number, expected_format="#YYXX"):
        self.badge_number = badge_number
        self.expected_format = expected_format
        message = f"Invalid badge number format: '{badge_number}'. Expected format: {expected_format}"
        super().__init__(message)


class ExcelImportError(TrackerException):
    """Raised when Excel import/export operations fail"""
    pass


class TemplateNotFoundError(ExcelImportError):
    """Raised when Excel template file is not found"""

    def __init__(self, template_path):
        self.template_path = template_path
        message = f"Excel template not found at: {template_path}"
        super().__init__(message)
