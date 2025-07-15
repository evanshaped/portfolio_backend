from django.contrib import admin

from .models import *

admin.site.register([Language, Corpus, Idiom, SearchSession, SearchFailure])