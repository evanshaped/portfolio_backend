import uuid
from django.db import models
import os
from django.conf import settings

class Language(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"

def get_default_language():
    lang, created = Language.objects.get_or_create(name='English (US)')
    return lang.id   # type: ignore (pylance is complaining that Langauge.id is not recognized)

class Idiom(models.Model):
    text = models.TextField()
    language = models.ForeignKey(Language, on_delete=models.SET_DEFAULT, default=get_default_language)
    regex = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.text} (regex {self.regex})" if self.regex else f"{self.text}"

class Corpus(models.Model):
    name = models.CharField(max_length=100)
    chunks_directory = models.CharField(max_length=255)
    total_chunks = models.IntegerField()
    chunk_size_mb = models.IntegerField()
    language = models.ForeignKey(Language, on_delete=models.SET_DEFAULT, default=get_default_language)
    total_word_count = models.IntegerField()
    description = models.TextField()

    def __str__(self):
        return f"{self.name}"
    
    def get_chunks_path(self):
        return os.path.join(settings.CORPUS_DIR, self.chunks_directory)

class SearchSession(models.Model):
    search_id = models.UUIDField(default=uuid.uuid4, unique=True)
    corpus = models.ForeignKey(Corpus, on_delete=models.CASCADE)
    #idiom = models.ForeignKey(Idiom, on_delete=models.CASCADE)
    idiom_pattern = models.CharField(max_length=30)
    is_completed = models.BooleanField(default=False)
    failed_chunks = models.IntegerField(default=0)
    completed_chunks = models.IntegerField(default=0)
    total_matches = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.search_id} ({self.idiom_pattern} in {self.corpus.name})"

class SearchFailure(models.Model):
    searchsession = models.ForeignKey(SearchSession, on_delete=models.CASCADE)
    chunk_name = models.CharField(max_length=50)
    failure_message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Corpus {self.searchsession.corpus.name}, chunk {self.chunk_name}"