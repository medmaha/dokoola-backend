from django.contrib import admin
from unfold.admin import ModelAdmin

from ..models import Certificate


@admin.register(Certificate)
class CertificateAdminClass(ModelAdmin):
    list_display = (
        "public_id",
        "name",
        "organization",
        "published",
        "date_issued",
        "updated_at",
    )
