"""
Unit tests for bi-directional synchronization between Trainee and AdvancedStaff models.

Tests verify that:
1. Creating a Trainee automatically creates an AdvancedStaff record
2. Creating an AdvancedStaff automatically creates a Trainee record
3. Field updates sync between both models
4. No infinite loops occur during sync operations
5. Badge number normalization works correctly
"""

from django.test import TestCase
from tracker.models import Trainee, AdvancedStaff, Cohort


class SyncTest(TestCase):
    """Test suite for Trainee <-> AdvancedStaff synchronization."""

    def setUp(self):
        """Create test cohort before each test."""
        self.cohort = Cohort.objects.create(
            name="Test 2025 Spring",
            year=2025,
            semester="Spring",
            semester_order=1
        )

    def test_trainee_creates_advanced_staff(self):
        """Creating Trainee should auto-create corresponding AdvancedStaff."""
        trainee = Trainee.objects.create(
            badge_number="#2525",
            first_name="John",
            last_name="Doe",
            cohort=self.cohort
        )

        # Should auto-create AdvancedStaff (badge normalized to "2525")
        self.assertTrue(AdvancedStaff.objects.filter(badge_number="2525").exists())
        adv = AdvancedStaff.objects.get(badge_number="2525")

        # Verify fields synced correctly
        self.assertEqual(adv.first_name, "John")
        self.assertEqual(adv.last_name, "Doe")
        self.assertEqual(adv.role, "Trainee")  # Default role
        self.assertEqual(adv.badge_status, "badging_in_progress")  # Default status
        self.assertTrue(adv.is_active)

    def test_advanced_creates_trainee(self):
        """Creating AdvancedStaff should auto-create corresponding Trainee."""
        adv = AdvancedStaff.objects.create(
            badge_number="2526",
            first_name="Jane",
            last_name="Smith",
            role="Staff"
        )

        # Should auto-create Trainee (badge normalized to "#2526")
        self.assertTrue(Trainee.objects.filter(badge_number="#2526").exists())
        trainee = Trainee.objects.get(badge_number="#2526")

        # Verify fields synced correctly
        self.assertEqual(trainee.first_name, "Jane")
        self.assertEqual(trainee.last_name, "Smith")
        self.assertEqual(trainee.cohort, self.cohort)  # Current cohort
        self.assertTrue(trainee.is_active)

    def test_no_infinite_loop(self):
        """Verify no infinite recursion occurs during sync operations."""
        # Create trainee (triggers Trainee -> AdvancedStaff sync)
        trainee = Trainee.objects.create(
            badge_number="#2527",
            first_name="Bob",
            last_name="Jones",
            cohort=self.cohort
        )

        # Update AdvancedStaff (should sync back to Trainee without infinite loop)
        adv = AdvancedStaff.objects.get(badge_number="2527")
        adv.first_name = "Robert"
        adv.save()

        # Verify no duplicates created
        self.assertEqual(Trainee.objects.filter(badge_number="#2527").count(), 1)
        self.assertEqual(AdvancedStaff.objects.filter(badge_number="2527").count(), 1)

        # Verify sync worked
        trainee.refresh_from_db()
        self.assertEqual(trainee.first_name, "Robert")

    def test_field_sync_first_name(self):
        """Test that first_name updates sync between models."""
        trainee = Trainee.objects.create(
            badge_number="#2528",
            first_name="Alice",
            last_name="Brown",
            cohort=self.cohort
        )

        adv = AdvancedStaff.objects.get(badge_number="2528")

        # Update trainee first_name
        trainee.first_name = "Alicia"
        trainee.save()

        # Check AdvancedStaff updated
        adv.refresh_from_db()
        self.assertEqual(adv.first_name, "Alicia")

        # Update AdvancedStaff first_name
        adv.first_name = "Ali"
        adv.save()

        # Check Trainee updated
        trainee.refresh_from_db()
        self.assertEqual(trainee.first_name, "Ali")

    def test_field_sync_last_name(self):
        """Test that last_name updates sync between models."""
        trainee = Trainee.objects.create(
            badge_number="#2529",
            first_name="Charlie",
            last_name="Green",
            cohort=self.cohort
        )

        adv = AdvancedStaff.objects.get(badge_number="2529")

        # Update trainee last_name
        trainee.last_name = "Greene"
        trainee.save()

        # Check AdvancedStaff updated
        adv.refresh_from_db()
        self.assertEqual(adv.last_name, "Greene")

    def test_field_sync_is_active(self):
        """Test that is_active status syncs between models."""
        trainee = Trainee.objects.create(
            badge_number="#2530",
            first_name="David",
            last_name="White",
            cohort=self.cohort,
            is_active=True
        )

        adv = AdvancedStaff.objects.get(badge_number="2530")
        self.assertTrue(adv.is_active)

        # Deactivate trainee
        trainee.is_active = False
        trainee.save()

        # Check AdvancedStaff deactivated
        adv.refresh_from_db()
        self.assertFalse(adv.is_active)

        # Reactivate via AdvancedStaff
        adv.is_active = True
        adv.save()

        # Check Trainee reactivated
        trainee.refresh_from_db()
        self.assertTrue(trainee.is_active)

    def test_badge_normalization(self):
        """Test that badge numbers are normalized correctly during sync."""
        # Create with # prefix
        trainee1 = Trainee.objects.create(
            badge_number="#1000",
            first_name="Test1",
            last_name="User1",
            cohort=self.cohort
        )
        adv1 = AdvancedStaff.objects.get(badge_number="1000")
        self.assertEqual(adv1.badge_number, "1000")  # No # in AdvancedStaff

        # Create without # prefix
        adv2 = AdvancedStaff.objects.create(
            badge_number="2000",
            first_name="Test2",
            last_name="User2",
            role="Staff"
        )
        trainee2 = Trainee.objects.get(badge_number="#2000")
        self.assertEqual(trainee2.badge_number, "#2000")  # Has # in Trainee

    def test_update_does_not_duplicate(self):
        """Test that updating a record doesn't create duplicates."""
        trainee = Trainee.objects.create(
            badge_number="#3000",
            first_name="Original",
            last_name="Name",
            cohort=self.cohort
        )

        # Initial counts
        self.assertEqual(Trainee.objects.filter(badge_number="#3000").count(), 1)
        self.assertEqual(AdvancedStaff.objects.filter(badge_number="3000").count(), 1)

        # Update multiple times
        trainee.first_name = "Updated1"
        trainee.save()

        trainee.first_name = "Updated2"
        trainee.save()

        trainee.last_name = "NewName"
        trainee.save()

        # Verify no duplicates
        self.assertEqual(Trainee.objects.filter(badge_number="#3000").count(), 1)
        self.assertEqual(AdvancedStaff.objects.filter(badge_number="3000").count(), 1)

    def test_existing_record_not_duplicated(self):
        """Test that sync finds existing records instead of creating duplicates."""
        # Create AdvancedStaff first
        adv = AdvancedStaff.objects.create(
            badge_number="4000",
            first_name="Existing",
            last_name="Staff",
            role="Staff"
        )

        # Create matching Trainee (should find existing AdvancedStaff, not create new)
        trainee = Trainee.objects.create(
            badge_number="#4000",
            first_name="Existing",
            last_name="Staff",
            cohort=self.cohort
        )

        # Verify only one AdvancedStaff exists
        self.assertEqual(AdvancedStaff.objects.filter(badge_number="4000").count(), 1)

    def test_sync_respects_different_fields(self):
        """Test that non-synced fields remain independent."""
        trainee = Trainee.objects.create(
            badge_number="#5000",
            first_name="Independent",
            last_name="Fields",
            cohort=self.cohort
        )

        adv = AdvancedStaff.objects.get(badge_number="5000")

        # Change AdvancedStaff role (should NOT sync to Trainee)
        adv.role = "Faculty"
        adv.save()

        # Trainee has no role field, so no error should occur
        trainee.refresh_from_db()
        self.assertEqual(trainee.first_name, "Independent")  # Still works

        # Change AdvancedStaff badge_status (should NOT sync to Trainee)
        adv.badge_status = "issued_active"
        adv.save()

        trainee.refresh_from_db()
        self.assertEqual(trainee.first_name, "Independent")  # Still works
