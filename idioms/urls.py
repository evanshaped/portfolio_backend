from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

idioms_router = DefaultRouter()
idioms_router.register(r'languages', views.LanguageViewSet)
idioms_router.register(r'corpora', views.CorpusViewSet)
idioms_router.register(r'idioms', views.IdiomViewSet)
idioms_router.register(r'searchsessions', views.SearchSessionViewSet)
idioms_router.register(r'searchfailures', views.SearchFailureViewSet)

urlpatterns = [
    path('', include(idioms_router.urls)),
]