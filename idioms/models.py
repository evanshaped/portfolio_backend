from django.db import models

class Language(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"

def get_default_language():
    lang, created = Language.objects.get_or_create(name='English (US)')
    return lang.id

class Idiom(models.Model):
    text = models.TextField()
    language = models.ForeignKey(Language, on_delete=models.SET_DEFAULT, default=get_default_language)

    def __str__(self):
        return f"{self.text}"

class Regex(models.Model):
    text = models.TextField()
    idiom = models.ForeignKey(Idiom, on_delete=models.CASCADE)
    whenAdded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Regex is {self.text} for idiom {self.idiom}"

class Corpus(models.Model):
    name = models.CharField(max_length=100)
    text = models.TextField()
    language = models.ForeignKey(Language, on_delete=models.SET_DEFAULT, default=get_default_language)
    wordCount = models.IntegerField()
    description = models.TextField()

    def __str__(self):
        return f"{self.name}"