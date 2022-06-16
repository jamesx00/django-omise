from django.test import TestCase
from django.utils import timezone


from django_omise.models.core import Customer
from django_omise.models.schedule import Schedule

# Create your tests here.
class ManagerTestCase(TestCase):
    def setUp(self):
        self.create_customer()
        self.create_schedule()

    def create_customer(self):
        self.customer = Customer.objects.create(id="test_customer_id", livemode=False)

    def create_schedule(self):
        self.schedule = Schedule.objects.create(
            id="test_schedule_id",
            livemode=False,
            active=True,
            start_on=timezone.now(),
            end_on=timezone.now(),
        )

    def test_live_queryset(self):
        self.assertTrue(Customer.objects.live().filter(id=self.customer.id).exists())
        self.assertFalse(
            Customer.objects.deleted().filter(id=self.customer.id).exists()
        )

    def test_deleted_queryset(self):
        self.customer.deleted = True
        self.customer.save()
        self.assertTrue(Customer.objects.deleted().filter(id=self.customer.id).exists())
        self.assertFalse(Customer.objects.live().filter(id=self.customer.id).exists())

    def test_deletable_manager_not_deleted_queryset(self):
        self.assertTrue(
            Schedule.objects.not_deleted().filter(id=self.schedule.id).exists()
        )

    def test_deletable_manager_live_queryset(self):
        self.assertTrue(Schedule.objects.live().filter(id=self.schedule.id).exists())

    def test_deletable_manager_deleted_queryset(self):
        self.schedule.deleted = True
        self.schedule.save()
        self.assertFalse(Schedule.objects.live().filter(id=self.schedule.id).exists())
        self.assertTrue(Schedule.objects.deleted().filter(id=self.schedule.id).exists())
