from django.contrib import admin
from django.http import HttpRequest
from unfold.admin import ModelAdmin

from .models import User


@admin.register(User)
class UserAdmin(ModelAdmin):
    pass

    list_filter = ("is_staff", "is_active")
    search_fields = ("email", "username", "first_name", "last_name")
    list_display = ("name", "email", "account_type", "is_active", "gender")
    list_display_links = ["name", "email"]

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False
