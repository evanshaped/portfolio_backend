from django.contrib import admin

from .models import Language, Corpus, Idiom, Regex

admin.site.register([Language, Corpus, Idiom, Regex])