from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

core_router = DefaultRouter()
core_router.register(r'jobs', views.JobViewSet)
core_router.register(r'projects', views.ProjectViewSet)
core_router.register(r'technologies', views.TechnologyViewSet)

urlpatterns = [
    path('', include(core_router.urls)),
]