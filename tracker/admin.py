from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms
from django.db import models
from .models import Trainee, Task, SignOff, StaffProfile, UnsignLog, Cohort

class SignOffInline(admin.TabularInline):
    model = SignOff
    extra = 0
    readonly_fields = ('signed_at', 'signed_by')
    fields = ('task', 'signed_by', 'signed_at', 'score', 'notes')
    can_delete = False


class TraineeAdminForm(forms.ModelForm):
    """Custom form for Trainee admin with badge number auto-suggestion"""

    class Meta:
        model = Trainee
        fields = '__all__'
        help_texts = {
            'badge_number': 'Format: #YYXX (e.g., #2501). Will auto-suggest based on cohort.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add placeholder text for badge number field
        self.fields['badge_number'].widget.attrs.update({
            'placeholder': 'Select cohort to see suggestion',
            'id': 'id_badge_number',
        })

    class Media:
        js = ('admin/js/trainee_badge_suggest.js',)


@admin.register(Trainee)
class TraineeAdmin(admin.ModelAdmin):
    form = TraineeAdminForm
    list_display = ('badge_number', 'full_name', 'cohort', 'progress_display', 'is_active')
    list_filter = ('cohort', 'is_active', 'date_added')
    search_fields = ('badge_number', 'first_name', 'last_name')
    inlines = [SignOffInline]
    list_select_related = ('cohort',)

    def get_queryset(self, request):
        """Optimize queryset to avoid N+1 queries in admin list view"""
        from django.db.models import Count
        qs = super().get_queryset(request)
        return qs.select_related('cohort').annotate(signoff_count=Count('signoffs', distinct=True))

    def progress_display(self, obj):
        """Display progress using annotated count to avoid N+1 queries"""
        total_tasks = Task.objects.filter(is_active=True).count()
        if total_tasks == 0:
            return "0%"
        # Use annotated count if available, otherwise calculate normally
        if hasattr(obj, 'signoff_count'):
            progress = round((obj.signoff_count / total_tasks) * 100, 1)
        else:
            progress = obj.get_progress_percentage()
        return f"{progress}%"
    progress_display.short_description = 'Progress'

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('get-next-badge/<int:cohort_id>/',
                 self.admin_site.admin_view(self.get_next_badge_number),
                 name='trainee-get-next-badge'),
        ]
        return custom_urls + urls

    def get_next_badge_number(self, request, cohort_id):
        """AJAX endpoint to get the next available badge number for a cohort"""
        from django.http import JsonResponse
        import re

        try:
            cohort = Cohort.objects.get(id=cohort_id)
            year_prefix = str(cohort.year)[-2:]  # Last 2 digits of year

            # Get all badge numbers starting with this year
            existing_badges = Trainee.objects.filter(
                badge_number__startswith=f'#{year_prefix}'
            ).values_list('badge_number', flat=True)

            if not existing_badges:
                # No existing badges for this year, start with 01
                next_badge = f'#{year_prefix}01'
            else:
                # Extract numeric parts and find the highest
                max_num = 0
                for badge in existing_badges:
                    # Extract number after the year prefix (e.g., #2501 -> 01)
                    match = re.match(rf'#{year_prefix}(\d+)', badge)
                    if match:
                        num = int(match.group(1))
                        max_num = max(max_num, num)

                # Increment and format
                next_num = max_num + 1
                next_badge = f'#{year_prefix}{next_num:02d}'  # Pad with zeros

            return JsonResponse({'next_badge': next_badge})

        except Cohort.DoesNotExist:
            return JsonResponse({'error': 'Cohort not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class TaskAdminForm(forms.ModelForm):
    """Custom form to allow order conflicts (model's save() will auto-shift)"""
    class Meta:
        model = Task
        fields = '__all__'

    def clean_order(self):
        """
        Allow duplicate order numbers during form validation.
        The model's save() method will handle auto-shifting to resolve conflicts.
        """
        order = self.cleaned_data.get('order')

        # Check if this order conflicts with another task
        existing_task = Task.objects.filter(order=order).exclude(pk=self.instance.pk).first()

        if existing_task:
            # Instead of raising an error, add a message to help_text
            # The save() method will auto-shift other tasks
            self.instance._order_conflict_info = f"Will auto-shift '{existing_task.name}' and subsequent tasks"

        return order

    def validate_unique(self):
        """
        Skip unique validation for 'order' field.
        The model's save() method handles conflicts via auto-shifting.
        """
        from django.core.exceptions import ValidationError

        # Get fields to exclude from uniqueness validation
        exclude = self._get_validation_exclusions()
        exclude.add('order')  # Don't validate order uniqueness here

        # Validate uniqueness for all other fields
        try:
            self.instance.validate_unique(exclude=exclude)
        except ValidationError as e:
            self._update_errors(e)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    form = TaskAdminForm
    list_display = ('order', 'name', 'category', 'requires_score', 'minimum_score', 'is_active', 'authorized_count')
    list_filter = ('category', 'requires_score', 'is_active')
    search_fields = ('name', 'description')
    ordering = ('order',)
    filter_horizontal = ('authorized_signers',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('order', 'name', 'description', 'category', 'is_active'),
            'description': 'Order will auto-shift existing tasks if there\'s a conflict'
        }),
        ('Scoring Requirements', {
            'fields': ('requires_score', 'minimum_score'),
            'description': 'Set minimum score if this task requires a passing grade (e.g., 70.00 for 70%)'
        }),
        ('Permissions', {
            'fields': ('authorized_signers',),
            'description': 'Leave empty to allow all staff to sign off this task'
        }),
    )

    def save_model(self, request, obj, form, change):
        """Save with helpful message about auto-shifting"""
        super().save_model(request, obj, form, change)
        if hasattr(obj, '_order_conflict_info'):
            from django.contrib import messages
            messages.info(request, f"Task order saved. {obj._order_conflict_info}.")

    def authorized_count(self, obj):
        count = obj.authorized_signers.count()
        return f"{count} staff" if count > 0 else "All staff"
    authorized_count.short_description = 'Authorized Signers'

@admin.register(SignOff)
class SignOffAdmin(admin.ModelAdmin):
    list_display = ('trainee', 'task', 'signed_by', 'signed_at', 'score')
    list_filter = ('signed_at', 'task__category', 'signed_by')
    search_fields = ('trainee__badge_number', 'trainee__first_name', 'trainee__last_name', 'task__name')
    readonly_fields = ('signed_at',)
    list_select_related = ('trainee', 'task', 'signed_by')

    def get_queryset(self, request):
        """Optimize queryset to avoid N+1 queries"""
        qs = super().get_queryset(request)
        return qs.select_related('trainee', 'trainee__cohort', 'task', 'signed_by')

    def save_model(self, request, obj, form, change):
        if not obj.signed_by:
            obj.signed_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(UnsignLog)
class UnsignLogAdmin(admin.ModelAdmin):
    list_display = ('trainee', 'task', 'original_signed_by', 'original_signed_at', 'unsigned_by', 'unsigned_at')
    list_filter = ('unsigned_at', 'task__category')
    search_fields = ('trainee__badge_number', 'trainee__first_name', 'trainee__last_name', 'task__name')
    readonly_fields = ('trainee', 'task', 'original_signed_by', 'original_signed_at', 'original_score', 'original_notes', 'unsigned_by', 'unsigned_at')
    list_select_related = ('trainee', 'task', 'original_signed_by', 'unsigned_by')

    def get_queryset(self, request):
        """Optimize queryset to avoid N+1 queries"""
        qs = super().get_queryset(request)
        return qs.select_related('trainee', 'trainee__cohort', 'task', 'original_signed_by', 'unsigned_by')

    def has_add_permission(self, request):
        # Prevent manual creation of unsign logs
        return False

    def has_change_permission(self, request, obj=None):
        # Make logs read-only
        return False

class StaffProfileInline(admin.StackedInline):
    model = StaffProfile
    can_delete = False

class UserAdmin(BaseUserAdmin):
    inlines = (StaffProfileInline,)

@admin.register(Cohort)
class CohortAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'semester', 'start_date', 'end_date', 'is_current_display', 'trainee_count_display')
    list_filter = ('year', 'semester', 'is_current_override')
    search_fields = ('name',)
    ordering = ('-year', '-semester')

    def get_queryset(self, request):
        """Optimize queryset to avoid N+1 queries"""
        from django.db.models import Count
        qs = super().get_queryset(request)
        return qs.annotate(active_trainee_count=Count('trainees', filter=models.Q(trainees__is_active=True)))

    def is_current_display(self, obj):
        current = Cohort.get_current_cohort()
        if obj.is_current_override:
            return "✓ Current (Manual Override)"
        elif current and obj.id == current.id:
            return "✓ Current (Auto-Detected)"
        else:
            return "-"
    is_current_display.short_description = 'Current Status'

    def trainee_count_display(self, obj):
        # Use annotated count if available, otherwise query directly
        if hasattr(obj, 'active_trainee_count'):
            count = obj.active_trainee_count
        else:
            count = obj.trainees.filter(is_active=True).count()
        return f"{count} trainee{'s' if count != 1 else ''}"
    trainee_count_display.short_description = 'Active Trainees'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Customize admin site header
admin.site.site_header = "Trainee Badge Tracker Administration"
admin.site.site_title = "Trainee Tracker"
admin.site.index_title = "Welcome to Trainee Badge Tracker"
