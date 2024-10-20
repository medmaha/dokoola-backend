from unfold.admin import ModelAdmin
from django.contrib import admin
from . import models


@admin.register(models.Talent)
class TalentAdminClass(ModelAdmin):
    search_fields = ("phone", "country", "state", "district", "website")
