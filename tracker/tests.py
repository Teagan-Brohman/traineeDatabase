from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import json

from .models import Trainee, Task, SignOff, StaffProfile, UnsignLog, Cohort


class CohortModelTest(TestCase):
    """Test Cohort model functionality"""

    def setUp(self):
        self.spring_2025 = Cohort.objects.create(
            name="Spring 2025",
            year=2025,
            semester="Spring"
        )
        self.fall_2025 = Cohort.objects.create(
            name="Fall 2025",
            year=2025,
            semester="Fall"
        )

    def test_cohort_creation(self):
        """Test basic cohort creation"""
        self.assertEqual(self.spring_2025.name, "Spring 2025")
        self.assertEqual(self.spring_2025.year, 2025)
        self.assertEqual(self.spring_2025.semester, "Spring")

    def test_cohort_start_end_dates(self):
        """Test cohort date calculations"""
        self.assertEqual(self.spring_2025.start_date, date(2025, 1, 1))
        self.assertEqual(self.spring_2025.end_date, date(2025, 6, 30))
        self.assertEqual(self.fall_2025.start_date, date(2025, 7, 1))
        self.assertEqual(self.fall_2025.end_date, date(2025, 12, 31))

    def test_cohort_ordering(self):
        """Test cohorts are ordered by year and semester descending (Fall before Spring)"""
        cohorts = list(Cohort.objects.all())
        # Fall (semester_order=2) comes before Spring (semester_order=1) in descending order
        self.assertEqual(cohorts[0], self.fall_2025)
        self.assertEqual(cohorts[1], self.spring_2025)

    def test_get_current_cohort_manual_override(self):
        """Test manual override for current cohort"""
        self.spring_2025.is_current_override = True
        self.spring_2025.save()

        current = Cohort.get_current_cohort()
        self.assertEqual(current, self.spring_2025)


class TraineeModelTest(TestCase):
    """Test Trainee model functionality"""

    def setUp(self):
        self.cohort = Cohort.objects.create(
            name="Fall 2025",
            year=2025,
            semester="Fall"
        )
        self.trainee = Trainee.objects.create(
            badge_number="#2501",
            first_name="John",
            last_name="Doe",
            cohort=self.cohort
        )

    def test_trainee_creation(self):
        """Test basic trainee creation"""
        self.assertEqual(self.trainee.badge_number, "#2501")
        self.assertEqual(self.trainee.first_name, "John")
        self.assertEqual(self.trainee.last_name, "Doe")
        self.assertEqual(self.trainee.cohort, self.cohort)
        self.assertTrue(self.trainee.is_active)

    def test_trainee_full_name(self):
        """Test full_name property"""
        self.assertEqual(self.trainee.full_name, "Doe, John")

    def test_trainee_str(self):
        """Test string representation"""
        self.assertEqual(str(self.trainee), "#2501 - Doe, John")

    def test_progress_percentage_no_tasks(self):
        """Test progress calculation with no tasks"""
        self.assertEqual(self.trainee.get_progress_percentage(), 0)

    def test_progress_percentage_with_tasks(self):
        """Test progress calculation with tasks"""
        user = User.objects.create_user('staff', 'staff@test.com', 'password')

        # Create 4 tasks
        for i in range(1, 5):
            Task.objects.create(
                order=i,
                name=f"Task {i}",
                is_active=True
            )

        # Sign off 2 tasks
        task1 = Task.objects.get(order=1)
        task2 = Task.objects.get(order=2)

        SignOff.objects.create(trainee=self.trainee, task=task1, signed_by=user)
        SignOff.objects.create(trainee=self.trainee, task=task2, signed_by=user)

        # Should be 50% (2 out of 4)
        self.assertEqual(self.trainee.get_progress_percentage(), 50.0)


class TaskModelTest(TestCase):
    """Test Task model functionality"""

    def setUp(self):
        self.user = User.objects.create_user('staff', 'staff@test.com', 'password')
        self.task = Task.objects.create(
            order=1,
            name="Test Task",
            category="Testing",
            requires_score=True,
            minimum_score=Decimal('70.00')
        )

    def test_task_creation(self):
        """Test basic task creation"""
        self.assertEqual(self.task.order, 1)
        self.assertEqual(self.task.name, "Test Task")
        self.assertTrue(self.task.requires_score)
        self.assertEqual(self.task.minimum_score, Decimal('70.00'))

    def test_task_str(self):
        """Test string representation"""
        self.assertEqual(str(self.task), "1. Test Task")

    def test_can_user_sign_off_no_restrictions(self):
        """Test authorization when no specific signers are set"""
        self.assertTrue(self.task.can_user_sign_off(self.user))

    def test_can_user_sign_off_with_authorized_signers(self):
        """Test authorization with specific authorized signers"""
        authorized_user = User.objects.create_user('authorized', 'auth@test.com', 'password')
        self.task.authorized_signers.add(authorized_user)

        # Authorized user should be able to sign off
        self.assertTrue(self.task.can_user_sign_off(authorized_user))

        # Non-authorized user should not
        self.assertFalse(self.task.can_user_sign_off(self.user))

    def test_task_order_auto_shift(self):
        """Test automatic task order shifting on conflict"""
        # Create task at order 2
        task2 = Task.objects.create(order=2, name="Task 2")

        # Create another task at order 2 (should shift existing task)
        task2_new = Task.objects.create(order=2, name="Task 2 New")

        # Refresh from DB
        task2.refresh_from_db()

        # Original task should be shifted to order 3
        self.assertEqual(task2_new.order, 2)
        self.assertEqual(task2.order, 3)


class SignOffModelTest(TestCase):
    """Test SignOff model functionality"""

    def setUp(self):
        self.cohort = Cohort.objects.create(name="Fall 2025", year=2025, semester="Fall")
        self.user = User.objects.create_user('staff', 'staff@test.com', 'password')
        self.trainee = Trainee.objects.create(
            badge_number="#2501",
            first_name="John",
            last_name="Doe",
            cohort=self.cohort
        )
        self.task = Task.objects.create(order=1, name="Test Task")

    def test_signoff_creation(self):
        """Test basic sign-off creation"""
        signoff = SignOff.objects.create(
            trainee=self.trainee,
            task=self.task,
            signed_by=self.user,
            score="85",
            notes="Good job"
        )

        self.assertEqual(signoff.trainee, self.trainee)
        self.assertEqual(signoff.task, self.task)
        self.assertEqual(signoff.signed_by, self.user)
        self.assertEqual(signoff.score, "85")
        self.assertIsNotNone(signoff.signed_at)

    def test_signoff_unique_constraint(self):
        """Test unique constraint on trainee+task"""
        SignOff.objects.create(
            trainee=self.trainee,
            task=self.task,
            signed_by=self.user
        )

        # Attempting to create another sign-off for same trainee+task should fail
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            SignOff.objects.create(
                trainee=self.trainee,
                task=self.task,
                signed_by=self.user
            )


class SignOffViewTest(TestCase):
    """Test sign-off related views"""

    def setUp(self):
        self.client = Client()
        self.cohort = Cohort.objects.create(name="Fall 2025", year=2025, semester="Fall")
        self.user = User.objects.create_user('staff', 'staff@test.com', 'password')
        self.user.is_staff = True
        self.user.save()

        StaffProfile.objects.create(user=self.user, initials="ST", can_sign_off=True)

        self.trainee = Trainee.objects.create(
            badge_number="#2501",
            first_name="John",
            last_name="Doe",
            cohort=self.cohort
        )

        self.task = Task.objects.create(
            order=1,
            name="Test Task",
            requires_score=False
        )

        self.task_with_score = Task.objects.create(
            order=2,
            name="Quiz Task",
            requires_score=True,
            minimum_score=Decimal('70.00')
        )

    def test_trainee_list_requires_login(self):
        """Test trainee list requires authentication"""
        response = self.client.get(reverse('trainee_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_trainee_list_authenticated(self):
        """Test authenticated user can view trainee list"""
        self.client.login(username='staff', password='password')
        response = self.client.get(reverse('trainee_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.trainee.badge_number)

    def test_trainee_detail_view(self):
        """Test trainee detail view"""
        self.client.login(username='staff', password='password')
        response = self.client.get(
            reverse('trainee_detail', args=[self.trainee.badge_number])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.trainee.full_name)
        self.assertContains(response, self.task.name)

    def test_sign_off_task_success(self):
        """Test successful task sign-off"""
        self.client.login(username='staff', password='password')
        response = self.client.post(
            reverse('sign_off_task', args=[self.trainee.badge_number, self.task.id]),
            {'notes': 'Completed successfully'}
        )

        # Should redirect back to trainee detail
        self.assertEqual(response.status_code, 302)

        # Verify sign-off was created
        signoff = SignOff.objects.get(trainee=self.trainee, task=self.task)
        self.assertEqual(signoff.signed_by, self.user)
        self.assertEqual(signoff.notes, 'Completed successfully')

    def test_sign_off_task_with_score_validation(self):
        """Test sign-off validation for tasks requiring scores"""
        self.client.login(username='staff', password='password')

        # Try to sign off without score (should fail)
        response = self.client.post(
            reverse('sign_off_task', args=[self.trainee.badge_number, self.task_with_score.id]),
            {}
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            SignOff.objects.filter(trainee=self.trainee, task=self.task_with_score).exists()
        )

    def test_sign_off_task_with_valid_score(self):
        """Test sign-off with valid score"""
        self.client.login(username='staff', password='password')
        response = self.client.post(
            reverse('sign_off_task', args=[self.trainee.badge_number, self.task_with_score.id]),
            {'score': '85.5'}
        )

        self.assertEqual(response.status_code, 302)
        signoff = SignOff.objects.get(trainee=self.trainee, task=self.task_with_score)
        self.assertEqual(signoff.score, '85.5')

    def test_sign_off_task_with_insufficient_score(self):
        """Test sign-off fails with insufficient score"""
        self.client.login(username='staff', password='password')
        response = self.client.post(
            reverse('sign_off_task', args=[self.trainee.badge_number, self.task_with_score.id]),
            {'score': '65.0'}  # Below minimum of 70
        )

        # Should redirect with error
        self.assertEqual(response.status_code, 302)
        # Sign-off should not be created
        self.assertFalse(
            SignOff.objects.filter(trainee=self.trainee, task=self.task_with_score).exists()
        )

    def test_unsign_task_creates_audit_log(self):
        """Test that unsigning creates an audit log entry"""
        # Create a sign-off first
        signoff = SignOff.objects.create(
            trainee=self.trainee,
            task=self.task,
            signed_by=self.user,
            score="90",
            notes="Original notes"
        )
        original_signed_at = signoff.signed_at

        # Login and unsign
        self.client.login(username='staff', password='password')
        response = self.client.post(
            reverse('unsign_task', args=[self.trainee.badge_number, self.task.id]),
            {'reason': 'Test unsign'}
        )

        # Should redirect
        self.assertEqual(response.status_code, 302)

        # Sign-off should be deleted
        self.assertFalse(
            SignOff.objects.filter(trainee=self.trainee, task=self.task).exists()
        )

        # Audit log should exist
        log = UnsignLog.objects.get(trainee=self.trainee, task=self.task)
        self.assertEqual(log.original_signed_by, self.user)
        self.assertEqual(log.original_score, "90")
        self.assertEqual(log.original_notes, "Original notes")
        self.assertEqual(log.unsigned_by, self.user)
        self.assertEqual(log.reason, "Test unsign")

    def test_unauthorized_sign_off(self):
        """Test that unauthorized users cannot sign off restricted tasks"""
        # Create a task with specific authorized signers
        authorized_user = User.objects.create_user('authorized', 'auth@test.com', 'password')
        restricted_task = Task.objects.create(
            order=3,
            name="Restricted Task"
        )
        restricted_task.authorized_signers.add(authorized_user)

        # Login as non-authorized user
        self.client.login(username='staff', password='password')
        response = self.client.post(
            reverse('sign_off_task', args=[self.trainee.badge_number, restricted_task.id]),
            {}
        )

        # Should redirect with error
        self.assertEqual(response.status_code, 302)
        # Sign-off should not be created
        self.assertFalse(
            SignOff.objects.filter(trainee=self.trainee, task=restricted_task).exists()
        )


class ArchiveViewTest(TestCase):
    """Test archive-related views"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('staff', 'staff@test.com', 'password')
        self.user.is_staff = True
        self.user.save()

        # Create multiple cohorts
        self.cohort_2024 = Cohort.objects.create(name="Fall 2024", year=2024, semester="Fall")
        self.cohort_2025 = Cohort.objects.create(name="Fall 2025", year=2025, semester="Fall")
        self.cohort_2025.is_current_override = True
        self.cohort_2025.save()

        # Create trainees
        self.trainee_2024 = Trainee.objects.create(
            badge_number="#2401",
            first_name="Old",
            last_name="Trainee",
            cohort=self.cohort_2024
        )
        self.trainee_2025 = Trainee.objects.create(
            badge_number="#2501",
            first_name="Current",
            last_name="Trainee",
            cohort=self.cohort_2025
        )

    def test_archive_list_view(self):
        """Test archive list shows non-current cohorts"""
        self.client.login(username='staff', password='password')
        response = self.client.get(reverse('archive_list'))

        self.assertEqual(response.status_code, 200)
        # Should show 2024 cohort but not 2025
        self.assertContains(response, "Fall 2024")

    def test_archive_search(self):
        """Test archive search functionality"""
        self.client.login(username='staff', password='password')
        response = self.client.get(reverse('archive_list') + '?search=2401')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "#2401")

    def test_archive_detail_view(self):
        """Test viewing a specific archived cohort"""
        self.client.login(username='staff', password='password')
        response = self.client.get(
            reverse('archive_detail', args=[self.cohort_2024.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.trainee_2024.badge_number)


class BulkSignOffTestCase(TestCase):
    """Test bulk sign-off functionality"""

    def setUp(self):
        """Set up test data"""
        # Create cohort
        self.cohort = Cohort.objects.create(name="Fall 2025", year=2025, semester="Fall")

        # Create staff users
        self.staff_user = User.objects.create_user(
            username='staff',
            password='password',
            first_name='Staff',
            last_name='User',
            is_staff=True
        )

        self.other_staff = User.objects.create_user(
            username='other_staff',
            password='password',
            first_name='Other',
            last_name='Staff',
            is_staff=True
        )

        # Create trainees
        self.trainee1 = Trainee.objects.create(
            badge_number='#2501',
            first_name='Alice',
            last_name='Smith',
            cohort=self.cohort
        )

        self.trainee2 = Trainee.objects.create(
            badge_number='#2502',
            first_name='Bob',
            last_name='Jones',
            cohort=self.cohort
        )

        self.trainee3 = Trainee.objects.create(
            badge_number='#2503',
            first_name='Charlie',
            last_name='Brown',
            cohort=self.cohort
        )

        # Create tasks
        self.task1 = Task.objects.create(
            order=1,
            name='Onboarding',
            description='Complete onboarding',
            requires_score=False
        )

        self.task2 = Task.objects.create(
            order=2,
            name='Quiz 1',
            description='First quiz',
            requires_score=True,
            minimum_score=80
        )

        self.task3 = Task.objects.create(
            order=3,
            name='Safety Training',
            description='Safety course',
            requires_score=False
        )

        self.task4 = Task.objects.create(
            order=4,
            name='SOP Training',
            description='Standard procedures',
            requires_score=False
        )

        # Task with restricted signers
        self.restricted_task = Task.objects.create(
            order=5,
            name='Restricted Task',
            description='Only certain staff can sign off',
            requires_score=False
        )
        self.restricted_task.authorized_signers.add(self.other_staff)

    def test_bulk_signoff_multiple_trainees_one_task(self):
        """Test signing off multiple trainees on one task"""
        self.client.login(username='staff', password='password')

        data = {
            'trainee_ids': [self.trainee1.id, self.trainee2.id, self.trainee3.id],
            'task_ids': [self.task1.id],
            'scores': {},
            'notes': 'Completed together'
        }

        response = self.client.post(
            reverse('bulk_sign_off'),
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertTrue(result['success'])
        self.assertEqual(result['created'], 3)
        self.assertEqual(result['updated'], 0)

        # Verify signoffs were created
        self.assertEqual(SignOff.objects.filter(task=self.task1).count(), 3)

    def test_bulk_signoff_one_trainee_multiple_tasks(self):
        """Test signing off one trainee on multiple tasks"""
        self.client.login(username='staff', password='password')

        data = {
            'trainee_ids': [self.trainee1.id],
            'task_ids': [self.task1.id, self.task3.id, self.task4.id],
            'scores': {},
            'notes': 'Caught up on multiple tasks'
        }

        response = self.client.post(
            reverse('bulk_sign_off'),
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertTrue(result['success'])
        self.assertEqual(result['created'], 3)

        # Verify signoffs for trainee1
        self.assertEqual(
            SignOff.objects.filter(trainee=self.trainee1).count(),
            3
        )

    def test_bulk_signoff_with_scores(self):
        """Test bulk sign-off with score requirements"""
        self.client.login(username='staff', password='password')

        data = {
            'trainee_ids': [self.trainee1.id, self.trainee2.id],
            'task_ids': [self.task2.id],
            'scores': {str(self.task2.id): '95'},
            'notes': 'Both passed quiz'
        }

        response = self.client.post(
            reverse('bulk_sign_off'),
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertTrue(result['success'])
        self.assertEqual(result['created'], 2)

        # Verify scores were recorded
        signoff1 = SignOff.objects.get(trainee=self.trainee1, task=self.task2)
        signoff2 = SignOff.objects.get(trainee=self.trainee2, task=self.task2)
        self.assertEqual(signoff1.score, '95')
        self.assertEqual(signoff2.score, '95')

    def test_bulk_signoff_missing_required_score(self):
        """Test bulk sign-off fails when required score is missing"""
        self.client.login(username='staff', password='password')

        data = {
            'trainee_ids': [self.trainee1.id],
            'task_ids': [self.task2.id],
            'scores': {},  # Missing required score
            'notes': ''
        }

        response = self.client.post(
            reverse('bulk_sign_off'),
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertFalse(result['success'])
        self.assertEqual(len(result['errors']), 1)
        self.assertIn('Score required', result['errors'][0]['error'])

        # Verify no signoff was created
        self.assertEqual(SignOff.objects.filter(task=self.task2).count(), 0)

    def test_bulk_signoff_score_below_minimum(self):
        """Test bulk sign-off fails when score is below minimum"""
        self.client.login(username='staff', password='password')

        data = {
            'trainee_ids': [self.trainee1.id],
            'task_ids': [self.task2.id],
            'scores': {str(self.task2.id): '70'},  # Below minimum of 80
            'notes': ''
        }

        response = self.client.post(
            reverse('bulk_sign_off'),
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertFalse(result['success'])
        self.assertEqual(len(result['errors']), 1)
        self.assertIn('below minimum', result['errors'][0]['error'])

        # Verify no signoff was created
        self.assertEqual(SignOff.objects.filter(task=self.task2).count(), 0)

    def test_bulk_signoff_unauthorized_task(self):
        """Test bulk sign-off skips unauthorized tasks"""
        self.client.login(username='staff', password='password')

        data = {
            'trainee_ids': [self.trainee1.id],
            'task_ids': [self.restricted_task.id],
            'scores': {},
            'notes': ''
        }

        response = self.client.post(
            reverse('bulk_sign_off'),
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertTrue(result['success'])
        self.assertEqual(result['created'], 0)
        self.assertEqual(len(result['skipped']), 1)
        self.assertIn('Not authorized', result['skipped'][0]['reason'])

        # Verify no signoff was created
        self.assertEqual(SignOff.objects.filter(task=self.restricted_task).count(), 0)

    def test_bulk_signoff_update_existing(self):
        """Test bulk sign-off updates existing signoffs"""
        # Create existing signoff
        SignOff.objects.create(
            trainee=self.trainee1,
            task=self.task1,
            signed_by=self.other_staff,
            notes='Original notes'
        )

        self.client.login(username='staff', password='password')

        data = {
            'trainee_ids': [self.trainee1.id],
            'task_ids': [self.task1.id],
            'scores': {},
            'notes': 'Updated notes'
        }

        response = self.client.post(
            reverse('bulk_sign_off'),
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertTrue(result['success'])
        self.assertEqual(result['created'], 0)
        self.assertEqual(result['updated'], 1)

        # Verify signoff was updated
        signoff = SignOff.objects.get(trainee=self.trainee1, task=self.task1)
        self.assertEqual(signoff.signed_by, self.staff_user)
        self.assertEqual(signoff.notes, 'Updated notes')

    def test_bulk_signoff_empty_selection(self):
        """Test bulk sign-off fails with empty selection"""
        self.client.login(username='staff', password='password')

        data = {
            'trainee_ids': [],
            'task_ids': [],
            'scores': {},
            'notes': ''
        }

        response = self.client.post(
            reverse('bulk_sign_off'),
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        result = response.json()
        self.assertFalse(result['success'])

    def test_bulk_signoff_requires_login(self):
        """Test bulk sign-off requires authentication"""
        data = {
            'trainee_ids': [self.trainee1.id],
            'task_ids': [self.task1.id],
            'scores': {},
            'notes': ''
        }

        response = self.client.post(
            reverse('bulk_sign_off'),
            data=json.dumps(data),
            content_type='application/json'
        )

        # Should redirect to login
        self.assertEqual(response.status_code, 302)

    def test_bulk_signoff_invalid_json(self):
        """Test bulk sign-off handles invalid JSON"""
        self.client.login(username='staff', password='password')

        response = self.client.post(
            reverse('bulk_sign_off'),
            data='invalid json',
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        result = response.json()
        self.assertFalse(result['success'])
