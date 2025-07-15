from django.db import models

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