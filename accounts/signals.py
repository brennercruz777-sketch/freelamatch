from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ClientProfile, FreelancerProfile, User


@receiver(post_save, sender=User)
def create_profile_for_user(sender, instance, created, **kwargs):
    if not created:
        return
    if instance.role == User.Role.CLIENT:
        ClientProfile.objects.create(user=instance)
    elif instance.role == User.Role.FREELANCER:
        FreelancerProfile.objects.create(user=instance)