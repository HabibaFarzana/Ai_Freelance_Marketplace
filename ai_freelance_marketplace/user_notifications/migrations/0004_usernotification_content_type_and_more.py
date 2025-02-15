# Generated by Django 5.1.4 on 2025-01-30 14:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('user_notifications', '0003_alter_usernotification_recipient_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='usernotification',
            name='content_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='usernotification',
            name='notification_type',
            field=models.CharField(choices=[('bid_submit', 'New Bid Submitted'), ('hire_freelancer', 'Hired for Project'), ('new_message', 'New Chat Message'), ('file_upload', 'File Uploaded'), ('file_delete', 'File Deleted')], default='new_message', max_length=20),
        ),
        migrations.AddField(
            model_name='usernotification',
            name='object_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
