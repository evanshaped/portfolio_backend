from django.contrib import admin

from .models import Language, Corpus, Idiom

admin.site.register([Language, Corpus, Idiom])