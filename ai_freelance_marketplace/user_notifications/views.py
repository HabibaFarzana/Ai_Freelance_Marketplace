from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import UserNotification
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.csrf import ensure_csrf_cookie

@login_required
@ensure_csrf_cookie
def get_notifications(request):
    notifications = UserNotification.objects.filter(recipient=request.user, is_read=False)
    return JsonResponse([{
        'id': n.id,
        'message': n.message,
        'url': n.url,
        'timestamp': n.timestamp.isoformat(),
        'type': n.notification_type
    } for n in notifications], safe=False)
    
@login_required
def get_unread_count(request):
    count = UserNotification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'unread_count': count})

@login_required
@require_http_methods(["POST"])
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(UserNotification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'success': True})

@login_required
@require_http_methods(["POST"])
@ensure_csrf_cookie
def mark_notification_as_read(request, notification_id):
    try:
        notification = get_object_or_404(UserNotification, id=notification_id, recipient=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    

@login_required
@require_http_methods(["POST"])
def clear_all_notifications(request):
    UserNotification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'success': True})