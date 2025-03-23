from django.contrib import admin
from unfold.admin import ModelAdmin

from core import models


@admin.register(models.Category)
class CategoryModelAdmin(ModelAdmin):
    list_display = ["name", "parent"]
