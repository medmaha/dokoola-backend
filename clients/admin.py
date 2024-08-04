
from django.http import HttpRequest
from unfold.admin import ModelAdmin
from django.contrib import admin
from . import models

@admin.register(models.Client)
class ClientAdminClass(ModelAdmin):
    search_fields = ( 'phone', "country", "state", "district", 'website')
    list_display = ('name', "email", 'rating', 'phone', 'address', "website")


    def has_change_permission(self, *args, **kwargs) -> bool:
        return False