from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.ProfileUpdateView.as_view(), name='update_profile'),
    path('user/update/', views.UserUpdateView.as_view(), name='update_user'),
    path('register/', views.register, name='register'),
    # path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('express_interest/', views.dashboard, name='express_interest'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('client-dashboard/', views.client_dashboard, name='client_dashboard'),
    path('freelancer-dashboard/', views.freelancer_dashboard, name='freelancer_dashboard'),
    path('users/', views.user_list, name='user_list'),
    path('user/<int:user_id>/', views.user_profile, name='user_profile'),

]