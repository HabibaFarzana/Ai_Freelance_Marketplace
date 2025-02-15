from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, FreelancerProfile, ClientProfile

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'user_type', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'bio', 'profile_picture', 'full_name', 'location', 'interests')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'bio', 'profile_picture', 'full_name', 'location', 'interests')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(FreelancerProfile)
admin.site.register(ClientProfile)