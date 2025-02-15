from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Map to the 'home' view
    path('projects/', views.project_list, name='project_list'),  # Move project list to /projects/
    path('<int:pk>/', views.project_detail, name='project_detail'),
    path('create/', views.create_project, name='create_project'),
    path('projects/<int:project_id>/submit_bid/', views.submit_bid, name='submit_bid'),
    path('delete/<int:pk>/', views.project_delete, name='project_delete'),
    path('my-projects/', views.my_projects, name='my_projects'),
    path('search/', views.search_projects, name='search_projects'),
    path('express-interest/<int:project_id>/', views.express_interest, name='express_interest'),
    path('project/<int:pk>/delete/', views.project_delete, name='project_delete'),  
    path('<int:project_id>/submit_bid/', views.submit_bid, name='submit_bid'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),
    path('freelancer/<str:username>/', views.freelancer_profile, name='freelancer_profile'),
    path('project/<int:project_id>/hire/<int:freelancer_id>/', views.hire_freelancer, name='hire_freelancer'),
    path('project/<int:project_id>/complete/', views.mark_project_completed, name='mark_project_completed'),
    path('project/<int:project_id>/review/', views.submit_review, name='submit_review'),
    path('project/<int:pk>/start/', views.start_project, name='start_project'),
    path('project/<int:project_id>/update-status/', views.update_project_status, name='update_project_status'),
    path('project/<int:project_id>/confirm-completion/', views.confirm_project_completion, name='confirm_project_completion'),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    path('project/<int:pk>/rate/', views.add_rating, name='add_rating'),
    path('project/<int:pk>/clear-history/', views.clear_project_history, name='clear_project_history'),
    path('project/<int:project_id>/hire/<int:freelancer_id>/', views.hire_freelancer, name='hire_freelancer'),
    path('project/<int:pk>/update/', views.update_project, name='update_project'),


]

