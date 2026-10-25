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