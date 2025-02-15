from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from accounts.models import CustomUser, FreelancerProfile
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

User = get_user_model()

class Project(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('hired', 'Hired'),
        ('just_started', 'Just Started'),
        ('intermediate', 'Intermediate'),
        ('completed', 'Completed'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('incomplete', 'Incomplete'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    required_skills = models.TextField(blank=True, null=True)
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_projects')
    hired_freelancer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='hired_projects')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline = models.DateTimeField()
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    current_work_details = models.TextField(blank=True, null=True)
    client_cleared_history = models.BooleanField(default=False)
    freelancer_cleared_history = models.BooleanField(default=False)
   
    def __str__(self):
        return self.title

    def hire_freelancer(self, freelancer):
        self.hired_freelancer = freelancer
        self.status = 'hired'
        self.save()

    def mark_completed(self):
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
        
    def start_project(self):
        self.status = 'just_started'
        self.started_at = timezone.now()
        self.save()
    
    def update_status(self, new_status, work_details=None):
        valid_statuses = dict(self.STATUS_CHOICES)
        if new_status in valid_statuses:
            self.status = new_status
            if work_details:
                self.current_work_details = work_details
            if new_status == 'completed':
                self.completed_at = timezone.now()
            self.save()
            return True
        return False

    def get_required_skills(self):
        return [skill.strip() for skill in self.required_skills.split(',') if skill.strip()] if self.required_skills else []

    def repost_project(self):
            """Create a new project based on current project with reset status"""
            new_project = Project.objects.create(
                title=self.title,
                description=self.description,
                required_skills=self.required_skills,
                client=self.client,
                budget=self.budget,
                deadline=timezone.now() + timezone.timedelta(days=30),
                status='open'
            )
            return new_project

    def mark_as_incomplete(self):
        """Mark project as incomplete and notify relevant users"""
        self.status = 'incomplete'
        self.save()
        
        # Create notification for client
        from user_notifications.models import UserNotification
        UserNotification.objects.create(
            recipient=self.client,
            message=f"Your project '{self.title}' has been marked as incomplete due to a missed deadline.",
            notification_type='project_incomplete'
        )
        
        # If there's a hired freelancer, notify them too
        if self.hired_freelancer:
            UserNotification.objects.create(
                recipient=self.hired_freelancer,
                message=f"Project '{self.title}' has been marked as incomplete due to a missed deadline.",
                notification_type='project_incomplete'
            )
    
class ProjectUpdate(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='updates')
    details = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ('open', 'Open'),
        ('hired', 'Hired'),
        ('just_started', 'Just Started'),
        ('intermediate', 'Intermediate'),
        ('completed', 'Completed'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Update for {self.project.title} - {self.get_status_display()}"


class Freelancer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    skills = models.JSONField()  # Stores the freelancer's skills
    experience_years = models.PositiveIntegerField()

    def __str__(self):
        return self.user.username

class Bid(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='bids')
    freelancer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
         return f"Bid by {self.user.username} on {self.project.title}"

class Rating(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='ratings')
    rater = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings_given')
    rated_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings_received')
    score = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'rater')

    def __str__(self):
        return f"Rating by {self.rater.username} for {self.rated_user.username} on project {self.project.title}"


@receiver(post_save, sender=Rating)
@receiver(post_save, sender=Rating)
def update_freelancer_rating(sender, instance, created, **kwargs):
    if created and instance.rated_user.user_type == 'freelancer':
        freelancer_profile = instance.rated_user.freelancer_profile
        ratings = Rating.objects.filter(rated_user=instance.rated_user)
        avg_rating = ratings.aggregate(models.Avg('score'))['score__avg']
        freelancer_profile.average_rating = avg_rating
        freelancer_profile.save()

class ProjectInterest(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='interests')
    freelancer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='project_interests')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'freelancer')

    def __str__(self):
        return f"{self.freelancer.username} interested in {self.project.title}"

    