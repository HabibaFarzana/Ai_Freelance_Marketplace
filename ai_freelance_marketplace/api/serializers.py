from rest_framework import serializers
from accounts.models import CustomUser, FreelancerProfile, ClientProfile, Skill
from projects.models import Project, Bid, Review

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name']

class FreelancerProfileSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)

    class Meta:
        model = FreelancerProfile
        fields = ['id', 'hourly_rate', 'experience_years', 'skills']

class ClientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientProfile
        fields = ['id', 'company_name', 'industry']

class CustomUserSerializer(serializers.ModelSerializer):
    freelancer_profile = FreelancerProfileSerializer(read_only=True)
    client_profile = ClientProfileSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'user_type', 'bio', 'profile_picture', 'freelancer_profile', 'client_profile']

class ProjectSerializer(serializers.ModelSerializer):
    client = CustomUserSerializer(read_only=True)
    freelancer = CustomUserSerializer(read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'client', 'freelancer', 'status', 'budget', 'created_at', 'updated_at', 'deadline']

class BidSerializer(serializers.ModelSerializer):
    freelancer = CustomUserSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)

    class Meta:
        model = Bid
        fields = ['id', 'project', 'freelancer', 'amount', 'proposal', 'created_at']

class ReviewSerializer(serializers.ModelSerializer):
    reviewer = CustomUserSerializer(read_only=True)
    reviewee = CustomUserSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'project', 'reviewer', 'reviewee', 'rating', 'comment', 'created_at']