from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, FreelancerProfile, ClientProfile

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 'freelancer':
            FreelancerProfile.objects.get_or_create(user=instance)
        elif instance.user_type == 'client':
            ClientProfile.objects.get_or_create(user=instance)