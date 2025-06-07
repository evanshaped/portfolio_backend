from django.shortcuts import render
from rest_framework import viewsets
from .models import *
from .serializer import *

class LanguageViewSet(viewsets.ModelViewSet):
    queryset = Language.objects.all().order_by('name')
    serializer_class = LanguageSerializer

class CorpusViewSet(viewsets.ModelViewSet):
    queryset = Corpus.objects.all().order_by('wordCount')
    serializer_class = CorpusSerializer

class IdiomViewSet(viewsets.ModelViewSet):
    queryset = Idiom.objects.all().order_by('text')
    serializer_class = IdiomSerializer

class RegexViewSet(viewsets.ModelViewSet):
    queryset = Regex.objects.all().order_by('whenAdded')
    serializer_class = RegexSerializer