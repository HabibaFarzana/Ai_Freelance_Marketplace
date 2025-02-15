from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, Count, Max
from django.views.decorators.http import require_POST
from .models import Conversation, Message, Notification
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_protect

User = get_user_model()

@login_required
def user_list(request):
    users = User.objects.exclude(id=request.user.id).order_by('username')
    return render(request, 'messaging/user_list.html', {'users': users})

@login_required
def user_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    existing_conversation = Conversation.objects.filter(participants=request.user).filter(participants=user).first()
    return render(request, 'messaging/user_profile.html', {
        'profile_user': user,
        'existing_conversation': existing_conversation
    })

@login_required
def conversation_list(request):
    conversations = Conversation.objects.filter(participants=request.user).annotate(
        unread_count=Count('messages', filter=Q(messages__is_read=False) & ~Q(messages__sender=request.user)),
        last_message_time=Max('messages__timestamp')
    ).order_by('-last_message_time')

    for conversation in conversations:
        conversation.other_participant = conversation.participants.exclude(id=request.user.id).first()
        conversation.last_message = conversation.messages.order_by('-timestamp').first()

    return render(request, 'messaging/conversation_list.html', {'conversations': conversations})

@login_required
def conversation(request, conversation_id):
    conversation = get_object_or_404(
        Conversation, 
        id=conversation_id, 
        participants=request.user
    )
    
    # Get other participant
    other_user = conversation.participants.exclude(id=request.user.id).first()
    
    # Fetch all messages for this conversation
    messages = conversation.messages.all().order_by('timestamp')
    
    # Mark all unread messages as read
    messages.filter(is_read=False, sender=other_user).update(is_read=True)
    
    context = {
        'conversation': conversation,
        'other_user': other_user,
        'messages': messages,
        'current_user': request.user
    }
    
    return render(request, 'messaging/conversation.html', context)

@login_required
def start_conversation(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    conversation = Conversation.objects.filter(participants=request.user).filter(participants=other_user).first()
    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, other_user)
    return redirect('conversation', conversation_id=conversation.id)

@login_required
def delete_conversation(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    conversation.delete()
    return redirect('conversation_list')

@login_required
def get_new_messages(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    last_message_id = request.GET.get('last_message_id')
    new_messages = conversation.messages.filter(id__gt=last_message_id)
    
    messages_data = [{
        'id': msg.id,
        'sender': msg.sender.username,
        'content': msg.content,
        'timestamp': msg.timestamp.isoformat()
    } for msg in new_messages]
    
    return JsonResponse({'messages': messages_data})

@login_required
def get_unread_count(request):
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'unread_count': unread_count})

@login_required
@csrf_protect
@require_POST
def delete_message(request, message_id):
    try:
        # Ensure the user can only delete their own messages
        message = get_object_or_404(
            Message, 
            id=message_id, 
            sender=request.user
        )
        
        # Soft delete (optional)
        # message.is_deleted = True
        # message.save()
        
        # Hard delete
        message.delete()
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)