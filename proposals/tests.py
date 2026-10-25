from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from accounts.models import User
from jobs.models import Category, Job
from .models import Proposal
from .services import ProposalError, accept_proposal


class ProposalPermissionTests(TestCase):
    def setUp(self):
        self.cli = User.objects.create_user(
            username="cli", email="cli@t.com", password="x", role=User.Role.CLIENT,
        )
        self.outro_cli = User.objects.create_user(
            username="cli2", email="cli2@t.com", password="x", role=User.Role.CLIENT,
        )
        self.fre = User.objects.create_user(
            username="fre", email="fre@t.com", password="x", role=User.Role.FREELANCER,
        )
        self.cat = Category.objects.create(name="Web", slug="web")
        self.job = Job.objects.create(
            client=self.cli, category=self.cat, title="T", description="D",
            budget_min=100, budget_max=200, deadline=timezone.now().date(),
        )

    def _payload(self, amount="150"):
        return {"amount": amount, "deadline_days": 5, "message": "Posso entregar."}

    def test_client_cannot_propose(self):
        self.client.force_login(self.cli)
        response = self.client.get(reverse("proposal_create", args=[self.job.pk]))
        self.assertEqual(response.status_code, 403)

    def test_freelancer_can_propose(self):
        self.client.force_login(self.fre)
        response = self.client.post(
            reverse("proposal_create", args=[self.job.pk]), self._payload()
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Proposal.objects.count(), 1)

    def test_freelancer_cannot_propose_twice(self):
        self.client.force_login(self.fre)
        self.client.post(reverse("proposal_create", args=[self.job.pk]), self._payload("150"))
        response = self.client.post(
            reverse("proposal_create", args=[self.job.pk]), self._payload("180")
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Você já enviou uma proposta")
        self.assertEqual(Proposal.objects.count(), 1)

    def test_cannot_propose_on_closed_job(self):
        self.job.status = Job.Status.IN_PROGRESS
        self.job.save()
        self.client.force_login(self.fre)
        response = self.client.post(
            reverse("proposal_create", args=[self.job.pk]), self._payload()
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "não está mais aberto")

    def test_client_cannot_see_others_proposals(self):
        Proposal.objects.create(
            job=self.job, freelancer=self.fre, amount=150, deadline_days=5, message="x",
        )
        self.client.force_login(self.outro_cli)
        response = self.client.get(reverse("job_proposals", args=[self.job.pk]))
        self.assertEqual(response.status_code, 403)

    def test_owner_sees_proposals(self):
        Proposal.objects.create(
            job=self.job, freelancer=self.fre, amount=150, deadline_days=5, message="x",
        )
        self.client.force_login(self.cli)
        response = self.client.get(reverse("job_proposals", args=[self.job.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "fre")

class AcceptProposalTests(TestCase):
    def setUp(self):
        self.cli = User.objects.create_user(
            username="cli", email="cli@t.com", password="x", role=User.Role.CLIENT,
        )
        self.fre1 = User.objects.create_user(
            username="fre1", email="fre1@t.com", password="x", role=User.Role.FREELANCER,
        )
        self.fre2 = User.objects.create_user(
            username="fre2", email="fre2@t.com", password="x", role=User.Role.FREELANCER,
        )
        cat = Category.objects.create(name="Web", slug="web")
        self.job = Job.objects.create(
            client=self.cli, category=cat, title="T", description="D",
            budget_min=100, budget_max=200, deadline=timezone.now().date(),
        )
        self.p1 = Proposal.objects.create(
            job=self.job, freelancer=self.fre1, amount=150, deadline_days=5, message="a",
        )
        self.p2 = Proposal.objects.create(
            job=self.job, freelancer=self.fre2, amount=180, deadline_days=7, message="b",
        )

    def test_accept_sets_statuses(self):
        accept_proposal(self.p1)
        self.p1.refresh_from_db()
        self.p2.refresh_from_db()
        self.job.refresh_from_db()
        self.assertEqual(self.p1.status, Proposal.Status.ACCEPTED)
        self.assertEqual(self.p2.status, Proposal.Status.REJECTED)
        self.assertEqual(self.job.status, Job.Status.IN_PROGRESS)

    def test_accept_creates_thread(self):
        accept_proposal(self.p1)
        self.assertTrue(hasattr(self.job, "thread"))

    def test_cannot_accept_when_job_not_open(self):
        self.job.status = Job.Status.IN_PROGRESS
        self.job.save()
        with self.assertRaises(ProposalError):
            accept_proposal(self.p1)

    def test_cannot_accept_twice(self):
        accept_proposal(self.p1)
        with self.assertRaises(ProposalError):
            accept_proposal(self.p1)

    def test_accept_view_forbidden_for_non_owner(self):
        outro = User.objects.create_user(
            username="outro", email="o@t.com", password="x", role=User.Role.CLIENT,
        )
        self.client.force_login(outro)
        response = self.client.post(reverse("proposal_accept", args=[self.p1.pk]))
        self.assertEqual(response.status_code, 403)

    def test_accept_view_owner(self):
        self.client.force_login(self.cli)
        response = self.client.post(reverse("proposal_accept", args=[self.p1.pk]))
        self.assertEqual(response.status_code, 302)
        self.job.refresh_from_db()
        self.assertEqual(self.job.status, Job.Status.IN_PROGRESS)