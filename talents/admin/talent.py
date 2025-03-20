from django.contrib import admin
from unfold.admin import ModelAdmin

from ..models import Talent


@admin.register(Talent)
class TalentAdminClass(admin.ModelAdmin):
    list_display = (
        "public_id",
        "name",
        "title",
        "bits",
        "pricing",
        "badge",
        "updated_at",
    )
