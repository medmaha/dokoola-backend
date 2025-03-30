from django.contrib import admin
from unfold.admin import ModelAdmin

from jobs import models


@admin.register(models.Job)
class JobModelAdmin(ModelAdmin):
    list_display = [
        "__title__",
        "job_type",
        "status",
        "application_deadline",
        "is_third_party",
    ]

    sortable_by = ["application_deadline", "status", "is_third_party"]
    actions = ["invalidate_jobs"]
    search_fields = ["title", "description"]

    def invalidate_jobs(self, request, queryset):

        queryset.update(is_valid=False, published=False)

        message_bit = (
            "1 job was" if queryset.count() == 1 else f"{queryset.count()} jobs were"
        )
        self.message_user(request, f"{message_bit} successfully marked as invalid.")

    invalidate_jobs.short_description = "Invalidate selected jobs"
