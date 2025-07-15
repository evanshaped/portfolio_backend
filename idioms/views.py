from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import *
from .serializer import *
import random

class LanguageViewSet(viewsets.ModelViewSet):
    queryset = Language.objects.all().order_by('name')
    serializer_class = LanguageSerializer

class CorpusViewSet(viewsets.ModelViewSet):
    queryset = Corpus.objects.all().order_by('total_word_count')
    serializer_class = CorpusSerializer

class IdiomViewSet(viewsets.ModelViewSet):
    queryset = Idiom.objects.all().order_by('text')
    serializer_class = IdiomSerializer

    @action(detail=False, methods=['get'])
    def random(self, request):
        idiom_count = Idiom.objects.count()
        if idiom_count == 0:
            return Response({'error': 'No idioms found'}, status=404)

        random_index = random.randint(0, idiom_count - 1)
        random_idiom = Idiom.objects.all()[random_index]

        language_text = random_idiom.language.name if random_idiom.language else "unknown"

        return Response({
            "idiomText": random_idiom.text,
            "languageText": language_text,
            "definitionText": "Definition not yet implemented",
            "regexText": random_idiom.regex if random_idiom.regex else "Regex not yet implemented",
        })