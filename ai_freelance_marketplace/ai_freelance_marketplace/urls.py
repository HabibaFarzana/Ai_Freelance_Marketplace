#urls.py:

"""
URL configuration for ai_freelance_marketplace project.

The urlpatterns list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import home, index, login,register,edit_profile,profile_view
from django.views.generic import TemplateView
from projects.views import project_list, project_detail, create_project, update_project,delete_project,search_projects,express_interest,submit_bid,freelancer_profile,about,services,contact,add_rating,hire_freelancer,mark_project_completed,submit_review,start_project,update_project_status,confirm_project_completion,clear_project_history,hire_freelancer, repost_project
from messaging.views import  get_unread_count,user_list,user_profile,conversation_list,conversation,start_conversation,delete_conversation,get_new_messages,delete_message
# from . import views
from file_management import views
from file_management import views as file_views
from user_notifications import views as notification_views

urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('home/', home, name='home'),
    path('about/', about ,name='about'),
    path('services/', services, name='services'),
    path('contact/', contact, name='contact'),
    path('login/', login, name='login'),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('accounts.urls')),
    path('massaging/', include('messaging.urls')),
    path('massaging/', include('ai_features.urls')),
    path('projects/', project_list, name='project_list'),
    path('projects/create/', create_project, name='create_project'),
    path('projects/<int:pk>/', project_detail, name='project_detail'),
    path('delete_project/<int:project_id>/', delete_project, name='delete_project'),
    path('project/search/', search_projects, name='search_projects'),
    path('express-interest/<int:pk>/', express_interest, name='express_interest'),
    path('register/', register, name='register'),
    path('profile/', profile_view, name='profile_view'),
    path('profile/edit/', edit_profile, name='edit_profile'),

    path('submit_bid/<int:project_id>/', submit_bid, name='submit_bid'),
    path('freelancer/<str:username>/', freelancer_profile, name='freelancer_profile'),
    path('project/<int:pk>/rate/', add_rating, name='add_rating'),
    path('project/<int:project_id>/hire/<int:freelancer_id>/', hire_freelancer, name='hire_freelancer'),
    path('project/<int:project_id>/complete/', mark_project_completed, name='mark_project_completed'),
    path('project/<int:project_id>/review/', submit_review, name='submit_review'),
    path('project/<int:pk>/start/', start_project, name='start_project'),
    path('project/<int:project_id>/update-status/', update_project_status, name='update_project_status'),
    path('project/<int:project_id>/confirm-completion/', confirm_project_completion, name='confirm_project_completion'),
    path('project/<int:pk>/clear-history/', clear_project_history, name='clear_project_history'),
    path('project/<int:project_id>/hire/<int:freelancer_id>/', hire_freelancer, name='hire_freelancer'),
    path('project/<int:pk>/update/', update_project, name='update_project'),
    path('users/', user_list, name='user_list'),
    path('user/<int:user_id>/', user_profile, name='user_profile'),
    path('conversations/', conversation_list, name='conversation_list'),
    path('conversation/<int:conversation_id>/', conversation, name='conversation'),
    path('start_conversation/<int:user_id>/', start_conversation, name='start_conversation'),
    path('delete_conversation/<int:conversation_id>/', delete_conversation, name='delete_conversation'),
    path('get_new_messages/<int:conversation_id>/', get_new_messages, name='get_new_messages'),
    path('get_unread_count/', get_unread_count, name='get_unread_count'),
    path('delete_message/<int:message_id>/', delete_message, name='delete_message'),

    path('projects/<int:project_id>/files/', views.project_files, name='project_files'),
    path('files/<int:file_id>/download/', views.download_file, name='download_file'),
    
    path('api/notifications/', notification_views.get_notifications, name='get_notifications'),
    path('api/notifications/unread-count/', notification_views.get_unread_count, name='get_unread_count'),
    # path('api/notifications/<int:notification_id>/mark-read/', notification_views.mark_notification_as_read, name='mark_notification_as_read'),
    # path('api/notifications/<int:notification_id>/mark-read/', notification_views.mark_notification_as_read, name='mark_notification_as_read'),
    path('api/notifications/', notification_views.get_notifications, name='get_notifications'),
    path('api/notifications/<int:notification_id>/mark-read/', notification_views.mark_notification_as_read, name='mark_notification_as_read'),
    
    
    path('api/files/<int:file_id>/delete/', file_views.delete_file, name='delete_file'),
    path('api/projects/<int:project_id>/files/', file_views.project_files, name='api_project_files'),
    path('api/files/<int:file_id>/download/', file_views.download_file, name='api_download_file'),
    path('api/files/<int:file_id>/delete/', file_views.delete_file, name='api_delete_file'),

    path('api/notifications/clear-all/', notification_views.clear_all_notifications, name='clear_all_notifications'),

    # In urls.py
    path('project/<int:pk>/repost/', repost_project, name='repost_project'),
]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)