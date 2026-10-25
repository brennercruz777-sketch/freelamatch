from django.conf import settings
from django.db import models


class Thread(models.Model):
    job = models.OneToOneField(
        "jobs.Job",
        on_delete=models.CASCADE,
        related_name="thread",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Thread do job: {self.job.title}"

    def participants(self):
        """Retorna [cliente, freelancer_aceito] (ou só cliente se ainda não aceitou)."""
        job = self.job
        accepted = job.proposals.filter(status="accepted").select_related("freelancer").first()
        people = [job.client]
        if accepted:
            people.append(accepted.freelancer)
        return people

    def is_participant(self, user):
        return user in self.participants()


class Message(models.Model):
    thread = models.ForeignKey(
        Thread,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="messages_sent",
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.sender}: {self.body[:40]}"