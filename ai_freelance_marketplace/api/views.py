from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from accounts.models import CustomUser, FreelancerProfile, ClientProfile, Skill
from projects.models import Project, Bid, Review
from .serializers import (
    CustomUserSerializer, FreelancerProfileSerializer, ClientProfileSerializer,
    SkillSerializer, ProjectSerializer, BidSerializer, ReviewSerializer
)
from ai_features.dynamic_pricing import train_pricing_model, get_price_recommendation
from ai_features.project_matching import match_project_to_freelancers

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

class FreelancerProfileViewSet(viewsets.ModelViewSet):
    queryset = FreelancerProfile.objects.all()
    serializer_class = FreelancerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

class ClientProfileViewSet(viewsets.ModelViewSet):
    queryset = ClientProfile.objects.all()
    serializer_class = ClientProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticated]

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def submit_bid(self, request, pk=None):
        project = self.get_object()
        serializer = BidSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(project=project, freelancer=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['get'])
    def get_price_recommendation(self, request, pk=None):
        project = self.get_object()
        freelancer = request.user
        model = train_pricing_model(Project.objects.all())
        recommendation = get_price_recommendation(model, project, freelancer)
        return Response({'price_recommendation': recommendation})

    @action(detail=True, methods=['get'])
    def match_freelancers(self, request, pk=None):
        project = self.get_object()
        freelancers = CustomUser.objects.filter(user_type='freelancer')
        matches = match_project_to_freelancers(project, freelancers)
        serializer = CustomUserSerializer(
            [match[0] for match in matches], 
            many=True, 
            context={'request': request}
        )
        return Response(serializer.data)

class BidViewSet(viewsets.ModelViewSet):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer
    permission_classes = [permissions.IsAuthenticated]

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        project = get_object_or_404(Project, pk=self.request.data.get('project'))
        reviewee = get_object_or_404(CustomUser, pk=self.request.data.get('reviewee'))
        serializer.save(reviewer=self.request.user, project=project, reviewee=reviewee)