from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        CLIENT = "client", "Cliente"
        FREELANCER = "freelancer", "Freelancer"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        help_text="Define se o usuário é cliente ou freelancer.",
    )
    email = models.EmailField("e-mail", unique=True)

    def is_client(self) -> bool:
        return self.role == self.Role.CLIENT

    def is_freelancer(self) -> bool:
        return self.role == self.Role.FREELANCER

class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="client_profile")
    company = models.CharField(max_length=120, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"Cliente: {self.user.username}"


class FreelancerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="freelancer_profile")
    headline = models.CharField(max_length=120, blank=True)
    skills = models.CharField(max_length=255, blank=True, help_text="Separe por vírgulas.")
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"Freelancer: {self.user.username}"