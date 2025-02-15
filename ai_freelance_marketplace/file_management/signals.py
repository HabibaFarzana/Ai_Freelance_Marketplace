from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ProjectFile
from user_notifications.models import UserNotification
from django.urls import reverse

@receiver(post_save, sender=ProjectFile)
def create_file_upload_notification(sender, instance, created, **kwargs):
    if created:
        project = instance.project
        recipients = [project.client]
        if project.hired_freelancer and project.hired_freelancer != instance.uploaded_by:
            recipients.append(project.hired_freelancer)

        for recipient in recipients:
            if recipient != instance.uploaded_by:
                UserNotification.objects.create(
                    recipient=recipient,
                    sender=instance.uploaded_by,
                    message=f"New file '{instance.name}' uploaded to project '{project.title}'",
                    url=reverse('project_detail', kwargs={'pk': project.id}),
                    notification_type='file_upload'
                )

@receiver(post_delete, sender=ProjectFile)
def create_file_deletion_notification(sender, instance, **kwargs):
    project = instance.project
    recipients = [project.client]
    if project.hired_freelancer and project.hired_freelancer != instance.uploaded_by:
        recipients.append(project.hired_freelancer)

    for recipient in recipients:
        if recipient != instance.uploaded_by:
            UserNotification.objects.create(
                recipient=recipient,
                sender=instance.uploaded_by,
                message=f"File '{instance.name}' was deleted from project '{project.title}'",
                url=reverse('project_detail', kwargs={'pk': project.id}),
                notification_type='file_deletion'
            )