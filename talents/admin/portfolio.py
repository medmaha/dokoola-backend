from django.contrib import admin
from unfold.admin import ModelAdmin

from ..models import Portfolio


@admin.register(Portfolio)
class PortfolioAdminClass(ModelAdmin):
    list_display = ("public_id", "name", "published", "url", "image", "updated_at")
