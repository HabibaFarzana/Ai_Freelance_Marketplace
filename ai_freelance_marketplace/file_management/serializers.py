# file_management/serializers.py
from rest_framework import serializers
from .models import ProjectFile

class ProjectFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectFile
        fields = ['id', 'name', 'file', 'uploaded_at', 'uploaded_by']
        read_only_fields = ['uploaded_at', 'uploaded_by']