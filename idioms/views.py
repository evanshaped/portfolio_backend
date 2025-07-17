from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from .services.corpus_validation import validate_corpus_chunks
from .services.corpus_search import search_corpus_chunks_for_pattern
from .models import *
from .serializer import *
import random
import threading

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
            return Response({'error': 'No idioms found'}, status=400)

        random_index = random.randint(0, idiom_count - 1)
        random_idiom = Idiom.objects.all()[random_index]

        language_text = random_idiom.language.name if random_idiom.language else "unknown"

        return Response({
            "idiomText": random_idiom.text,
            "languageText": language_text,
            "definitionText": "Definition not yet implemented",
            "regexText": random_idiom.regex if random_idiom.regex else "Regex not yet implemented",
        })

class SearchSessionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SearchSession.objects.all().order_by('created_at')
    serializer_class = SearchSessionSerializer
    lookup_field = 'search_id'
    lookup_url_kwarg = 'search_id'

class SearchFailureViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SearchFailure.objects.all().order_by('created_at')
    serializer_class = SearchFailureSerializer

@api_view(['POST'])
def start_search(request):
    try:
        idiom_pattern = request.data.get('idiom_pattern')
    except KeyError:
        return Response({'error': 'Pattern required'}, status=400)
    
    try:
        corpus_id = request.data.get('corpus_id')
    except KeyError:
        return Response({'error': 'Corpus ID required'}, status=400)
    
    try:
        corpus = Corpus.objects.get(id=corpus_id)
    except Corpus.DoesNotExist:
        return Response({'error': f'Corpus {corpus_id} not found'}, status=400)

    try:
        validate_corpus_chunks(corpus)
    except Exception as e:
        return Response({'error': e}, status=400)
    
    search = SearchSession.objects.create(
        corpus=corpus, 
        idiom_pattern=idiom_pattern
    )

    thread = threading.Thread(
        target=search_corpus_chunks_for_pattern,
        args=(search.search_id,),
    )
    thread.daemon = True
    thread.start()

    return Response({'search_id': str(search.search_id)})