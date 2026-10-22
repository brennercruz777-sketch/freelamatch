from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from accounts.models import User
from jobs.models import Category, Job
from .models import Proposal


class ProposalConstraintTests(TestCase):
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

    def test_duplicate_proposal_blocked(self):
        Proposal.objects.create(
            job=self.job, freelancer=self.fre, amount=150, deadline_days=5, message="ok",
        )
        with self.assertRaises(IntegrityError):
            Proposal.objects.create(
                job=self.job, freelancer=self.fre, amount=200, deadline_days=7, message="dup",
            )