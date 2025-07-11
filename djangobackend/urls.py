"""
URL configuration for djangobackend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
import core.views
import idioms.views

core_router = routers.DefaultRouter()
core_router.register(r'jobs', core.views.JobViewSet)
core_router.register(r'projects', core.views.ProjectViewSet)
core_router.register(r'technologies', core.views.TechnologyViewSet)

idioms_router = routers.DefaultRouter()
idioms_router.register(r'languages', idioms.views.LanguageViewSet)
idioms_router.register(r'corpora', idioms.views.CorpusViewSet)
idioms_router.register(r'idioms', idioms.views.IdiomViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("core-api/", include(core_router.urls)),
    path("idioms-api/", include(idioms_router.urls)),
]
