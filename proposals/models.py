from django.conf import settings
from django.db import models
from django.urls import reverse


class Proposal(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendente"
        ACCEPTED = "accepted", "Aceita"
        REJECTED = "rejected", "Rejeitada"
        WITHDRAWN = "withdrawn", "Retirada"

    job = models.ForeignKey(
        "jobs.Job",
        on_delete=models.CASCADE,
        related_name="proposals",
    )
    freelancer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="proposals",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    deadline_days = models.PositiveIntegerField()
    message = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["job", "freelancer"],
                name="unique_proposal_per_freelancer",
            )
        ]

    def __str__(self):
        return f"{self.freelancer} → {self.job} ({self.amount})"

    def get_absolute_url(self):
        return reverse("job_detail", args=[self.job.pk])