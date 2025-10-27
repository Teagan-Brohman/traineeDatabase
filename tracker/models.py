from django.db import models, transaction
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from datetime import date

class Cohort(models.Model):
    """Represents a training cohort (e.g., Fall 2025, Spring 2026)"""
    SEMESTER_CHOICES = [
        ('Spring', 'Spring'),
        ('Fall', 'Fall'),
    ]

    SEMESTER_ORDER = {
        'Spring': 1,  # First half of year
        'Fall': 2,    # Second half of year
    }

    name = models.CharField(max_length=50, unique=True, db_index=True, help_text="e.g., Fall 2025")
    year = models.IntegerField(db_index=True)
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES, db_index=True)
    semester_order = models.IntegerField(default=1, db_index=True, help_text="Numeric order for sorting: Spring=1, Fall=2")
    is_current_override = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Manually set this cohort as current (overrides automatic detection)"
    )

    class Meta:
        ordering = ['-year', '-semester_order']  # Year descending, then Fall before Spring
        unique_together = ['year', 'semester']
        indexes = [
            models.Index(fields=['-year', '-semester_order'], name='cohort_year_semester_idx'),
        ]

    def save(self, *args, **kwargs):
        """Auto-set semester_order based on semester"""
        self.semester_order = self.SEMESTER_ORDER.get(self.semester, 1)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def start_date(self):
        """Calculate cohort start date based on semester"""
        if self.semester == 'Spring':
            return date(self.year, 1, 1)
        else:  # Fall
            return date(self.year, 7, 1)

    @property
    def end_date(self):
        """Calculate cohort end date based on semester"""
        if self.semester == 'Spring':
            return date(self.year, 6, 30)
        else:  # Fall
            return date(self.year, 12, 31)

    def is_current(self):
        """Check if this cohort is current based on today's date"""
        today = date.today()
        return self.start_date <= today <= self.end_date

    @classmethod
    def get_current_cohort(cls):
        """Get the current cohort (override takes precedence)"""
        # Check for manual override first
        override = cls.objects.filter(is_current_override=True).first()
        if override:
            return override

        # Auto-detect based on today's date
        today = date.today()
        for cohort in cls.objects.all():
            if cohort.is_current():
                return cohort

        # If no current cohort found, return the most recent one
        return cls.objects.first()

class Trainee(models.Model):
    badge_number = models.CharField(max_length=20, unique=True, db_index=True)
    first_name = models.CharField(max_length=100, db_index=True)
    last_name = models.CharField(max_length=100, db_index=True)
    cohort = models.ForeignKey(Cohort, on_delete=models.PROTECT, related_name='trainees', db_index=True)
    date_added = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ['badge_number']
        indexes = [
            models.Index(fields=['cohort', 'is_active'], name='trainee_cohort_active_idx'),
            models.Index(fields=['last_name', 'first_name'], name='trainee_name_idx'),
        ]

    def __str__(self):
        return f"{self.badge_number} - {self.last_name}, {self.first_name}"

    @property
    def full_name(self):
        return f"{self.last_name}, {self.first_name}"

    def get_progress_percentage(self):
        """Calculate percentage of tasks completed"""
        total_tasks = Task.objects.filter(is_active=True).count()
        if total_tasks == 0:
            return 0
        completed_tasks = SignOff.objects.filter(trainee=self).values('task').distinct().count()
        return round((completed_tasks / total_tasks) * 100, 1)


class Task(models.Model):
    order = models.IntegerField(unique=True, db_index=True, help_text="Display order (must be unique)")
    name = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True, max_length=10000)
    category = models.CharField(max_length=100, blank=True, db_index=True, help_text="e.g., Security, Safety, Documentation")
    requires_score = models.BooleanField(default=False, help_text="Does this task require a quiz score?")
    minimum_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum passing score (only applies if task requires a score)"
    )
    is_active = models.BooleanField(default=True, db_index=True)
    authorized_signers = models.ManyToManyField(
        User,
        blank=True,
        related_name='authorized_tasks',
        help_text="Specific staff members authorized to sign off this task. Leave empty to allow all staff."
    )

    class Meta:
        ordering = ['order']
        indexes = [
            models.Index(fields=['is_active', 'order'], name='task_active_order_idx'),
            models.Index(fields=['category', 'is_active'], name='task_category_active_idx'),
        ]

    def __str__(self):
        return f"{self.order}. {self.name}"

    def can_user_sign_off(self, user):
        """Check if a user is authorized to sign off this task"""
        # If no specific signers are set, any authenticated staff can sign off
        if not self.authorized_signers.exists():
            return True
        # Otherwise, check if user is in the authorized list
        return self.authorized_signers.filter(id=user.id).exists()

    @transaction.atomic
    def save(self, *args, **kwargs):
        """Auto-shift task orders when there's a conflict"""
        # Check if this is a new task or if order changed
        if self.pk:
            # Existing task - check if order changed
            try:
                old_task = Task.objects.get(pk=self.pk)
                order_changed = old_task.order != self.order
                old_order = old_task.order
            except Task.DoesNotExist:
                order_changed = False
                old_order = None
        else:
            # New task
            order_changed = True
            old_order = None

        if order_changed:
            # Check if there's already a task at this order position
            conflict_exists = Task.objects.filter(order=self.order).exclude(pk=self.pk).exists()

            if conflict_exists:
                # Only shift if there's an actual conflict
                # Temporarily move existing task to a safe position to avoid conflicts
                if old_order is not None:
                    Task.objects.filter(pk=self.pk).update(order=999999)

                # Shift all tasks at or after this position up by 1
                tasks_to_shift = Task.objects.filter(order__gte=self.order).exclude(pk=self.pk).order_by('-order')
                for task in tasks_to_shift:
                    Task.objects.filter(pk=task.pk).update(order=task.order + 1)

        super().save(*args, **kwargs)


class SignOff(models.Model):
    # Score validator: allows decimal numbers like "95", "95.5", "100.00"
    score_validator = RegexValidator(
        regex=r'^\d+(\.\d{1,2})?$',
        message='Score must be a valid number (e.g., 95, 95.5, 100.00)'
    )

    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE, related_name='signoffs', db_index=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='signoffs', db_index=True)
    signed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='signoffs_given', db_index=True)
    signed_at = models.DateTimeField(auto_now_add=True, db_index=True)
    notes = models.TextField(blank=True, max_length=10000, help_text="Any comments or notes")
    score = models.CharField(max_length=20, blank=True, validators=[score_validator], help_text="Quiz score if applicable (e.g., 95, 95.5)")

    class Meta:
        unique_together = ['trainee', 'task']
        ordering = ['-signed_at']
        indexes = [
            models.Index(fields=['trainee', 'signed_at'], name='signoff_trainee_date_idx'),
            models.Index(fields=['signed_by', 'signed_at'], name='signoff_signer_date_idx'),
        ]

    def __str__(self):
        return f"{self.trainee.badge_number} - {self.task.name} - {self.signed_by}"


class StaffProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    initials = models.CharField(max_length=10, help_text="Staff initials for quick identification")
    can_sign_off = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.initials})"


class UnsignLog(models.Model):
    """Audit trail for removed sign-offs"""
    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE, related_name='unsign_logs', db_index=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='unsign_logs', db_index=True)
    original_signed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='original_signoffs_removed',
        db_index=True,
        help_text="Who originally signed off"
    )
    original_signed_at = models.DateTimeField(db_index=True, help_text="When original sign-off occurred")
    original_score = models.CharField(max_length=20, blank=True)
    original_notes = models.TextField(blank=True, max_length=10000)
    unsigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='unsign_actions',
        db_index=True,
        help_text="Who removed the sign-off"
    )
    unsigned_at = models.DateTimeField(auto_now_add=True, db_index=True)
    reason = models.TextField(blank=True, max_length=10000, help_text="Reason for removal")

    class Meta:
        ordering = ['-unsigned_at']
        indexes = [
            models.Index(fields=['trainee', '-unsigned_at'], name='unsignlog_trainee_date_idx'),
            models.Index(fields=['unsigned_by', '-unsigned_at'], name='unsignlog_unsigner_date_idx'),
        ]

    def __str__(self):
        return f"Unsigned: {self.trainee.badge_number} - {self.task.name} by {self.unsigned_by}"


# ============================================================================
# Advanced Training Models
# ============================================================================
# These models track advanced training for staff members (separate from
# orientation/trainee tracking). Imported from ADV_TrainingStatus_WIP.xlsx.
# ============================================================================

class AdvancedStaff(models.Model):
    """Staff member receiving advanced training (separate from trainee orientation)"""

    ROLE_CHOICES = [
        ('Operator', 'Operator'),
        ('Student', 'Student'),
        ('Trainee', 'Trainee'),
        ('Staff', 'Staff'),
        ('Faculty', 'Faculty'),
        ('HP', 'Health Physics'),
        ('Other', 'Other'),
    ]

    badge_number = models.CharField(max_length=20, unique=True, db_index=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True, help_text="False for removed/past staff")

    class Meta:
        ordering = ['badge_number']
        verbose_name = 'Advanced Training Staff'
        verbose_name_plural = 'Advanced Training Staff'
        indexes = [
            models.Index(fields=['is_active', 'role'], name='adv_staff_active_role_idx'),
        ]

    def __str__(self):
        return f"{self.badge_number} - {self.get_full_name()} ({self.role})"

    def get_full_name(self):
        return f"{self.last_name}, {self.first_name}"

    @property
    def full_name(self):
        return self.get_full_name()


class AdvancedTrainingType(models.Model):
    """Types of advanced training (KP, Escort, ExpSamp, Other)"""

    name = models.CharField(max_length=100, unique=True)
    order = models.IntegerField(default=0, help_text="Display order")
    allows_custom_type = models.BooleanField(
        default=False,
        help_text="True for 'Other Training' categories that have custom type field"
    )
    is_active = models.BooleanField(default=True)
    authorized_signers = models.ManyToManyField(
        User,
        blank=True,
        related_name='authorized_advanced_training_types',
        help_text="Specific staff members authorized to sign off this training type. Leave empty to allow all staff."
    )

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Advanced Training Type'
        verbose_name_plural = 'Advanced Training Types'

    def __str__(self):
        return self.name

    def can_user_sign_off(self, user):
        """Check if a user is authorized to sign off this training type"""
        # If no specific signers are set, any authenticated staff can sign off
        if not self.authorized_signers.exists():
            return True
        # Otherwise, check if user is in the authorized list
        return self.authorized_signers.filter(id=user.id).exists()


class AdvancedTraining(models.Model):
    """Completed advanced training record for a staff member"""

    staff = models.ForeignKey(
        AdvancedStaff,
        on_delete=models.CASCADE,
        related_name='trainings',
        db_index=True
    )
    training_type = models.ForeignKey(
        AdvancedTrainingType,
        on_delete=models.CASCADE,
        related_name='trainings',
        db_index=True
    )

    # Training completion details
    completion_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Date training was completed"
    )
    approver_initials = models.CharField(
        max_length=10,
        blank=True,
        help_text="Initials of staff who approved (e.g., 'ET', 'AS')"
    )
    termination_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date training expires or was terminated"
    )

    # For "Other Training" types that need custom categorization
    custom_type = models.CharField(
        max_length=100,
        blank=True,
        help_text="Custom type for 'Other Training' (e.g., 'Package', 'Experiment', 'Waste')"
    )

    # Additional metadata
    notes = models.TextField(blank=True, max_length=10000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-completion_date']
        verbose_name = 'Advanced Training Record'
        verbose_name_plural = 'Advanced Training Records'
        # Unique constraint: One training record per staff+type combo
        # (custom_type allows multiple "Other" trainings with different types)
        unique_together = ['staff', 'training_type', 'custom_type']
        indexes = [
            models.Index(fields=['staff', 'training_type'], name='adv_train_staff_type_idx'),
            models.Index(fields=['completion_date'], name='adv_train_completion_idx'),
            models.Index(fields=['termination_date'], name='adv_train_termination_idx'),
        ]

    def __str__(self):
        type_name = f"{self.training_type.name}"
        if self.custom_type:
            type_name += f" ({self.custom_type})"
        return f"{self.staff.badge_number} - {type_name}"

    @property
    def is_expired(self):
        """Check if training has expired based on termination date"""
        if not self.termination_date or not self.completion_date:
            return False
        from datetime import date
        return date.today() > self.termination_date

    def is_expiring_soon(self, days=30):
        """Check if training expires within specified days"""
        if not self.termination_date or not self.completion_date:
            return False
        from datetime import date, timedelta
        return date.today() <= self.termination_date <= (date.today() + timedelta(days=days))
