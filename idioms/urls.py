from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

idioms_router = DefaultRouter()
idioms_router.register(r'languages', views.LanguageViewSet)
idioms_router.register(r'corpora', views.CorpusViewSet)
idioms_router.register(r'idioms', views.IdiomViewSet)

urlpatterns = [
    path('', include(idioms_router.urls)),
]