from django.shortcuts import render
from rest_framework import viewsets
from .models import *
from .serializer import *

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all().order_by('start_date')
    serializer_class = JobSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by('start_date')
    serializer_class = ProjectSerializer

class TechnologyViewSet(viewsets.ModelViewSet):
    queryset = Technology.objects.all().order_by('name')
    serializer_class = TechnologySerializer