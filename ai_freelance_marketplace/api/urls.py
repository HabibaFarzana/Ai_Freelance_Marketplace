from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomUserViewSet, FreelancerProfileViewSet, ClientProfileViewSet,
    SkillViewSet, ProjectViewSet, BidViewSet, ReviewViewSet
)

router = DefaultRouter()
router.register(r'users', CustomUserViewSet)
router.register(r'freelancer-profiles', FreelancerProfileViewSet)
router.register(r'client-profiles', ClientProfileViewSet)
router.register(r'skills', SkillViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'bids', BidViewSet)
router.register(r'reviews', ReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
]