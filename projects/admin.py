
from unfold.admin import ModelAdmin
from django.contrib import admin
from . import models

@admin.register(models.Project)
class ProjectsAdminClass(ModelAdmin):
    pass     