from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.user_list, name='user_list'),
    path('user/<int:user_id>/', views.user_profile, name='user_profile'),
    path('conversations/', views.conversation_list, name='conversation_list'),
    path('conversation/<int:conversation_id>/', views.conversation, name='conversation'),
    path('start_conversation/<int:user_id>/', views.start_conversation, name='start_conversation'),
    path('delete_conversation/<int:conversation_id>/', views.delete_conversation, name='delete_conversation'),
    path('get_new_messages/<int:conversation_id>/', views.get_new_messages, name='get_new_messages'),
    path('get_unread_count/', views.get_unread_count, name='get_unread_count'),
    path('delete_message/<int:message_id>/', views.delete_message, name='delete_message'),
]