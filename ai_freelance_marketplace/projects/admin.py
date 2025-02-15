from django.contrib import admin
from .models import Project, Bid, Rating, ProjectUpdate

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'hired_freelancer', 'status', 'budget', 'created_at', 'deadline')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description', 'client__username', 'hired_freelancer__username')

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('project', 'freelancer', 'amount', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('project__title', 'freelancer__username')

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('project', 'rater', 'rated_user', 'score', 'created_at')
    list_filter = ('score', 'created_at')
    search_fields = ('project__title', 'rater__username', 'rated_user__username', 'comment')

@admin.register(ProjectUpdate)
class ProjectUpdateAdmin(admin.ModelAdmin):
    list_display = ('project', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('project__title', 'details')

# Remove or comment out the following lines if they exist:
# admin.site.register(Freelancer)
# admin.site.register(ProjectInterest)

