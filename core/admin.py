from django.contrib import admin

from .models import Job, Project, Technology

admin.site.register([Job, Project, Technology])