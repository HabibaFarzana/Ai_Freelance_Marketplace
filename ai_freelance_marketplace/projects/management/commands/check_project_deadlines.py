# Create new file: projects/management/commands/check_project_deadlines.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from projects.models import Project
class Command(BaseCommand):
    help = 'Check and update status of projects past their deadline'

    def handle(self, *args, **kwargs):
        current_time = timezone.now()
        
        # Get all projects that are past deadline and not already completed/cancelled/incomplete
        overdue_projects = Project.objects.filter(
            deadline__lt=current_time,
            status__in=['open', 'hired', 'just_started', 'intermediate']
        )
        
        for project in overdue_projects:
            project.mark_as_incomplete()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully marked project "{project.title}" as incomplete'
                )
            )