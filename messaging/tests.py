from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from jobs.models import Category, Job
from proposals.models import Proposal
from proposals.services import accept_proposal
from .models import Message


class ThreadPermissionTests(TestCase):
    def setUp(self):
        self.cli = User.objects.create_user(
            username="cli", email="cli@t.com", password="x", role=User.Role.CLIENT,
        )
        self.fre = User.objects.create_user(
            username="fre", email="fre@t.com", password="x", role=User.Role.FREELANCER,
        )
        self.outro = User.objects.create_user(
            username="outro", email="o@t.com", password="x", role=User.Role.FREELANCER,
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
        self.thread = self.job.thread

    def test_client_can_access(self):
        self.client.force_login(self.cli)
        response = self.client.get(reverse("thread_detail", args=[self.thread.pk]))
        self.assertEqual(response.status_code, 200)

    def test_freelancer_aceito_can_access(self):
        self.client.force_login(self.fre)
        response = self.client.get(reverse("thread_detail", args=[self.thread.pk]))
        self.assertEqual(response.status_code, 200)

    def test_outro_freelancer_forbidden(self):
        self.client.force_login(self.outro)
        response = self.client.get(reverse("thread_detail", args=[self.thread.pk]))
        self.assertEqual(response.status_code, 403)

    def test_participant_can_send_message(self):
        self.client.force_login(self.cli)
        self.client.post(reverse("message_create", args=[self.thread.pk]), {"body": "oi"})
        self.assertEqual(Message.objects.count(), 1)