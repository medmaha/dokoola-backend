from django.contrib import admin
from unfold.admin import ModelAdmin

from . import models


@admin.register(models.Talent)
class TalentAdminClass(ModelAdmin):
    search_fields = ("phone", "country", "state", "district", "website")
