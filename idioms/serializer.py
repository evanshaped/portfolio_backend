from rest_framework import serializers
from .models import Idiom, Language, Corpus, Regex

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
        fields = ['text']

class RegexSerializer(serializers.ModelSerializer):
    class Meta:
        model = Regex
        fields = ['text', 'idiom', 'whenAdded']