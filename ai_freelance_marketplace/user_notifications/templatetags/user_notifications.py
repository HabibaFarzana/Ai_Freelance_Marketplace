from django import template
from user_notifications.models import UserNotification

register = template.Library()

@register.inclusion_tag('user_notifications/notification_list.html', takes_context=True)
def user_notifications(context):
    request = context['request']
    notifications = UserNotification.objects.filter(recipient=request.user, is_read=False).order_by('-timestamp')[:5]
    return {'notifications': notifications}

@register.simple_tag(takes_context=True)
def user_notification_count(context):
    request = context['request']
    count = UserNotification.objects.filter(recipient=request.user, is_read=False).count()
    return f'({count})' if count > 0 else ''