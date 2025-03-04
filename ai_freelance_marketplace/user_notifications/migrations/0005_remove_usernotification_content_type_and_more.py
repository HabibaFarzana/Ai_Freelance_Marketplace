# Generated by Django 5.1.4 on 2025-01-30 15:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_notifications', '0004_usernotification_content_type_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usernotification',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='usernotification',
            name='notification_type',
        ),
        migrations.RemoveField(
            model_name='usernotification',
            name='object_id',
        ),
        migrations.AlterField(
            model_name='usernotification',
            name='recipient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_notifications', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='usernotification',
            name='sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_notifications', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='usernotification',
            name='url',
            field=models.CharField(default='/', max_length=255),
        ),
    ]
