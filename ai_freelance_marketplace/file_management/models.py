# file_management/models.py
from django.db import models
from django.conf import settings
from notifications.signals import notify
from django.db.models.signals import post_save
from django.dispatch import receiver
# from user_notifications.models import UserNotification


class ProjectFile(models.Model):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='project_files/')
    name = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def can_delete(self, user):
        """Check if user has permission to delete the file"""
        return user == self.uploaded_by

    def notify_upload(self):
        """Send notification to project participants about new file"""
        recipients = []
        if self.project.client != self.uploaded_by:
            recipients.append(self.project.client)
        if self.project.hired_freelancer and self.project.hired_freelancer != self.uploaded_by:
            recipients.append(self.project.hired_freelancer)
        
        for recipient in recipients:
            notify.send(
                sender=self.uploaded_by,
                recipient=recipient,
                verb='uploaded',
                action_object=self,
                target=self.project,
                description=f'New file uploaded: {self.name}'
            )
            
            
    def __str__(self):
        return self.name

# @receiver(post_save, sender=ProjectFile)
# def create_file_notification(sender, instance, created, **kwargs):
#     if created:
#         project = instance.project
#         recipient = project.client if instance.uploaded_by == project.hired_freelancer else project.hired_freelancer
#         if recipient:
#             UserNotification.objects.create(
#                 recipient=recipient,
#                 sender=instance.uploaded_by,
#                 message=f"New file '{instance.name}' uploaded to project '{project.title}'",
#             )