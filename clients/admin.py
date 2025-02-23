from django.contrib import admin
from django.http import HttpRequest
from unfold.admin import ModelAdmin

from . import models


@admin.register(models.Client)
class ClientAdminClass(ModelAdmin):
    search_fields = ("phone", "country", "state", "district", "website")

    # def has_change_permission(self, *args, **kwargs) -> bool:
    #     return False
