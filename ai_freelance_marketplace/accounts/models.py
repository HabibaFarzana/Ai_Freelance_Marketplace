from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('client', 'Client'),
        ('freelancer', 'Freelancer'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='client')
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    interests = models.TextField(blank=True)

class FreelancerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='freelancer_profile')
    working_profession = models.CharField(max_length=255, blank=True)
    skills = models.TextField(blank=True, default='')
    average_rating = models.FloatField(default=0.0)
    description = models.TextField(blank=True)
    completed_projects_count = models.PositiveIntegerField(default=0)

    def get_skills_list(self):
        return [skill.strip() for skill in self.skills.split(',') if skill.strip()]

    def set_skills_list(self, skills_list):
        self.skills = ', '.join(skills_list)

class ClientProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='client_profile')
    company_name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

