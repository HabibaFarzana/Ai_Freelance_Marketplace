from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from .models import Bid, Project, ProjectUpdate
from user_notifications.models import UserNotification

@receiver(post_save, sender=Project)
def create_project_status_notification(sender, instance, created, **kwargs):
    """Handle all project status-related notifications"""
    if not created and instance.status:  # Only for status updates, not new projects
        notification_data = {
            'incomplete': {
                'message': f"Project '{instance.title}' has been marked as incomplete due to missed deadline",
                'notification_type': 'project_incomplete',
                'recipients': [instance.client, instance.hired_freelancer] if instance.hired_freelancer else [instance.client]
            },
            'hired': {
                'message': f"You've been hired for the project '{instance.title}'",
                'notification_type': 'hired',
                'recipients': [instance.hired_freelancer] if instance.hired_freelancer else []
            },
            'just_started': {
                'message': f"Project '{instance.title}' has been started",
                'notification_type': 'project_started',
                'recipients': [instance.client]
            },
            'completed': {
                'message': f"Project '{instance.title}' has been marked as completed",
                'notification_type': 'project_completed',
                'recipients': [instance.client]
            }
        }

        if instance.status in notification_data:
            data = notification_data[instance.status]
            url = reverse('project_detail', kwargs={'pk': instance.id})
            
            for recipient in data['recipients']:
                if recipient:  # Ensure recipient exists
                    UserNotification.objects.create(
                        recipient=recipient,
                        sender=instance.hired_freelancer if instance.status != 'incomplete' else None,
                        message=data['message'],
                        url=url,
                        notification_type=data['notification_type']
                    )

@receiver(post_save, sender=Bid)
def create_bid_notification(sender, instance, created, **kwargs):
    """Handle bid notifications"""
    if created:
        UserNotification.objects.create(
            recipient=instance.project.client,
            sender=instance.freelancer,
            message=f"New bid on your project '{instance.project.title}'",
            url=reverse('project_detail', kwargs={'pk': instance.project.id}),
            notification_type='new_bid'
        )

@receiver(post_save, sender=ProjectUpdate)
def create_project_update_notification(sender, instance, created, **kwargs):
    """Handle project update notifications"""
    if created:
        UserNotification.objects.create(
            recipient=instance.project.client,
            sender=instance.project.hired_freelancer,
            message=f"Status update for project '{instance.project.title}': {instance.get_status_display()}",
            url=reverse('project_detail', kwargs={'pk': instance.project.id}),
            notification_type='project_update'
        )