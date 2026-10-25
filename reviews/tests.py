from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from jobs.models import Category, Job
from proposals.models import Proposal
from proposals.services import accept_proposal
from .models import Review


class ReviewRulesTests(TestCase):
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
        )
        prop = Proposal.objects.create(
            job=self.job, freelancer=self.fre, amount=150, deadline_days=5, message="a",
        )
        accept_proposal(prop)

    def _complete_job(self):
        self.job.status = Job.Status.COMPLETED
        self.job.completed_at = timezone.now()
        self.job.save()

    def test_cannot_review_open_job(self):
        self.client.force_login(self.cli)
        response = self.client.get(reverse("review_create", args=[self.job.pk]))
        self.assertEqual(response.status_code, 302)  # redireciona

    def test_client_can_review_after_complete(self):
        self._complete_job()
        self.client.force_login(self.cli)
        response = self.client.post(
            reverse("review_create", args=[self.job.pk]),
            {"rating": "5", "comment": "Ótimo"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(Review.objects.first().reviewee, self.fre)

    def test_freelancer_can_review_after_complete(self):
        self._complete_job()
        self.client.force_login(self.fre)
        response = self.client.post(
            reverse("review_create", args=[self.job.pk]),
            {"rating": "4", "comment": "Bom cliente"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.first().reviewee, self.cli)

    def test_cannot_review_twice(self):
        self._complete_job()
        self.client.force_login(self.cli)
        self.client.post(reverse("review_create", args=[self.job.pk]), {"rating": "5", "comment": "a"})
        response = self.client.post(reverse("review_create", args=[self.job.pk]), {"rating": "4", "comment": "b"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.count(), 1)