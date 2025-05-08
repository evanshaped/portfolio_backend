from rest_framework import serializers
from .models import Job, Project, Technology

class TechnologySerializer(serializers.ModelSerializer):
    class Meta:
        model = Technology
        fields = ['name', 'url']

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['job_title', 'company_name', 'start_date', 'end_date', 'description']

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['title', 'job', 'description', 'difficulty_rating', 'start_date']