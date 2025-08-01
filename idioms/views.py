from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.decorators import action, api_view, permission_classes
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

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def random(self, request):
        idiom_count = Idiom.objects.count()
        if idiom_count == 0:
            return Response({'error': 'No idioms found'}, status=400)

        random_index = random.randint(0, idiom_count - 1)
        random_idiom = Idiom.objects.all()[random_index]

        serializer = self.get_serializer(random_idiom)
        return Response(serializer.data)

class SearchSessionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SearchSession.objects.all().order_by('created_at')
    serializer_class = SearchSessionSerializer
    lookup_field = 'search_id'
    lookup_url_kwarg = 'search_id'

    @action(detail=True, methods=['get'])
    def matches(self, request, *args, **kwargs):
        search_session = self.get_object()
        matches = RegexMatch.objects.filter(searchsession=search_session)
        serializer = RegexMatchSerializer(matches, many=True)
        return Response(serializer.data)

class SearchFailureViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SearchFailure.objects.all().order_by('created_at')
    serializer_class = SearchFailureSerializer

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def start_search(request):
    idiom_id = request.data.get('idiom_id')
    custom_regex_pattern = request.data.get('custom_regex_pattern')
    if not idiom_id and not custom_regex_pattern:
        return Response({'error': 'Either idiom_id or custom_regex_pattern required to initiate search'}, status=400)
    if idiom_id and custom_regex_pattern:
        return Response({'error': 'Only provide one of either idiom_id or custom_regex_pattern'}, status=400)

    corpus_id = request.data.get('corpus_id')
    if corpus_id is None:
        return Response({'error': 'Corpus ID required'}, status=400)
    try:
        corpus = Corpus.objects.get(id=corpus_id)
    except Corpus.DoesNotExist:
        return Response({'error': f'Corpus {corpus_id} not found'}, status=400)
    try:
        validate_corpus_chunks(corpus)
    except Exception as e:
        return Response({'error': e}, status=400)
    
    if idiom_id:
        try:
            idiom = Idiom.objects.get(id=idiom_id)
            search = SearchSession.objects.create(
                corpus=corpus,
                idiom=idiom,
            )
        except Idiom.DoesNotExist:
            return Response({'error': f'Idiom {idiom_id} not found'}, status=400)
    else:
        custom_regex = CustomRegex.objects.create(
            regex = custom_regex_pattern,
        )
        search = SearchSession.objects.create(
            corpus=corpus,
            custom_regex=custom_regex,
        )
    
    thread = threading.Thread(
        target=search_corpus_chunks_for_pattern,
        args=(search.search_id,),
    )
    thread.daemon = True
    thread.start()

    return Response({'search_id': str(search.search_id)})