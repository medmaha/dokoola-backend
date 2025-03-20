from django.contrib import admin
from unfold.admin import ModelAdmin

from ..models import Education


@admin.register(Education)
class EducationAdminClass(ModelAdmin):
    list_display = (
        "public_id",
        "degree",
        "institution",
        "published",
        "start_date",
        "end_date",
        "updated_at",
    )
