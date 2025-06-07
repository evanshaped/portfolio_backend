from django.db import models

class Language(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"

class Corpus(models.Model):
    name = models.CharField(max_length=100)
    text = models.TextField()
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True)
    wordCount = models.IntegerField(default=0)
    description = models.TextField()

    def __str__(self):
        return f"{self.name}"

class Idiom(models.Model):
    text = models.TextField()
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.text}"

class Regex(models.Model):
    text = models.TextField()
    idiom = models.ForeignKey(Idiom, on_delete=models.SET_NULL, null=True, blank=True)
    whenAdded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Regex is {self.text} for idiom {self.idiom}"