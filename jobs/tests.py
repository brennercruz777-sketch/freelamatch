from django.test import TestCase
from django.utils import timezone

from accounts.models import User
from .models import Category, Job


class JobModelTests(TestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(
            username="cli", email="cli@test.com", password="x", role=User.Role.CLIENT,
        )
        self.cat = Category.objects.create(name="Web", slug="web")

    def test_job_defaults_to_open(self):
        job = Job.objects.create(
            client=self.client_user,
            category=self.cat,
            title="T",
            description="D",
            budget_min=100,
            budget_max=200,
            deadline=timezone.now().date(),
        )
        self.assertEqual(job.status, Job.Status.OPEN)
        self.assertTrue(job.is_open)