from django.test import TestCase
from django.utils import timezone
from accounts.models import User
from .models import Category, Job
from django.urls import reverse

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

class JobPermissionTests(TestCase):
    def setUp(self):
        self.cli = User.objects.create_user(
            username="cli", email="cli@t.com", password="x", role=User.Role.CLIENT,
        )
        self.fre = User.objects.create_user(
            username="fre", email="fre@t.com", password="x", role=User.Role.FREELANCER,
        )
        self.cat = Category.objects.create(name="Web", slug="web")
        self.job = Job.objects.create(
            client=self.cli, category=self.cat, title="T", description="D",
            budget_min=100, budget_max=200, deadline=timezone.now().date(),
        )

    def test_anonymous_cannot_create_job(self):
        response = self.client.get(reverse("job_create"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_freelancer_cannot_create_job(self):
        self.client.force_login(self.fre)
        response = self.client.get(reverse("job_create"))
        self.assertEqual(response.status_code, 403)

    def test_client_can_create_job(self):
        self.client.force_login(self.cli)
        response = self.client.get(reverse("job_create"))
        self.assertEqual(response.status_code, 200)

    def test_freelancer_cannot_edit_others_job(self):
        self.client.force_login(self.fre)
        response = self.client.get(reverse("job_update", args=[self.job.pk]))
        self.assertEqual(response.status_code, 403)

    def test_client_cannot_edit_others_job(self):
        outro = User.objects.create_user(
            username="cli2", email="cli2@t.com", password="x", role=User.Role.CLIENT,
        )
        self.client.force_login(outro)
        response = self.client.get(reverse("job_update", args=[self.job.pk]))
        self.assertEqual(response.status_code, 403)

    def test_list_public_accessible(self):
        response = self.client.get(reverse("job_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "T")

class JobCompleteTests(TestCase):
    def setUp(self):
        self.cli = User.objects.create_user(
            username="cli", email="cli@t.com", password="x", role=User.Role.CLIENT,
        )
        self.fre = User.objects.create_user(
            username="fre", email="fre@t.com", password="x", role=User.Role.FREELANCER,
        )
        cat = Category.objects.create(name="Web", slug="web")
        self.job = Job.objects.create(
            client=self.cli, category=cat, title="T", description="D",
            budget_min=100, budget_max=200, deadline=timezone.now().date(),
            status=Job.Status.IN_PROGRESS,
        )

    def test_only_owner_can_complete(self):
        self.client.force_login(self.fre)
        response = self.client.post(reverse("job_complete", args=[self.job.pk]))
        self.assertEqual(response.status_code, 403)

    def test_complete_sets_completed_at(self):
        self.client.force_login(self.cli)
        response = self.client.post(reverse("job_complete", args=[self.job.pk]))
        self.assertEqual(response.status_code, 302)
        self.job.refresh_from_db()
        self.assertEqual(self.job.status, Job.Status.COMPLETED)
        self.assertIsNotNone(self.job.completed_at)

    def test_cannot_complete_open_job(self):
        self.job.status = Job.Status.OPEN
        self.job.save()
        self.client.force_login(self.cli)
        self.client.post(reverse("job_complete", args=[self.job.pk]))
        self.job.refresh_from_db()
        self.assertEqual(self.job.status, Job.Status.OPEN)