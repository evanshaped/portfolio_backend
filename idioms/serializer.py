from rest_framework import serializers
from .models import *

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['id', 'name']

class CorpusSerializer(serializers.ModelSerializer):
    language_name = serializers.CharField(source='language.name', read_only=True)
    class Meta:
        model = Corpus
        fields = [
            'id', 'name', 'chunks_directory', 'total_chunks', 
            'chunk_size_mb', 'language_name', 
            'total_word_count', 'description',
        ]

class IdiomSerializer(serializers.ModelSerializer):
    language_name = serializers.CharField(source='language.name', read_only=True)
    class Meta:
        model = Idiom
        fields = ['id', 'text', 'language_name', 'regex']

class SearchSessionSerializer(serializers.ModelSerializer):
    corpus_name = serializers.CharField(source='corpus.name', read_only=True)
    total_chunks = serializers.CharField(source='corpus.total_chunks', read_only=True)
    progress = serializers.SerializerMethodField()
    def get_progress(self, obj):
        return ((obj.completed_chunks + obj.failed_chunks) / obj.total_chunks)
    class Meta:
        model = SearchSession
        fields = [
            'search_id', 'corpus_name', 'total_chunks', 
            'idiom_pattern', 'is_completed', 'failed_chunks', 
            'completed_chunks', 'total_matches', 'created_at',
            'progress',
        ]

class SearchFailureSerializer(serializers.ModelSerializer):
    search_id = serializers.IntegerField(source='searchsession.search_id', read_only=True)
    corpus_name = serializers.CharField(source='searchsession.corpus.name', read_only=True)
    idiom_pattern = serializers.CharField(source='searchsession.idiom_pattern', read_only=True)
    class Meta:
        model = SearchFailure
        fields = ['search_id', 'corpus_name', 'idiom_pattern', 'chunk_name', 'failure_message', 'created_at']