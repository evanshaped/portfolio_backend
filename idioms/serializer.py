from rest_framework import serializers
from .models import Idiom, Language, Corpus

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['name']

class CorpusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Corpus
        fields = ['name', 'text', 'language', 'wordCount', 'description']

class IdiomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Idiom
        fields = ['text', 'language', 'regex']