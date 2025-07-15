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