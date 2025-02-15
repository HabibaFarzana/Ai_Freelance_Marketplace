from django.urls import path
from . import views
from .recommendation_system import recommend_projects

urlpatterns = [
    path('recommend_projects/', recommend_projects, name='recommend_projects'),
]