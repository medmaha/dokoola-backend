from django.contrib import admin
from unfold.admin import ModelAdmin

from jobs import models


@admin.register(models.Activities)
class ActivityModelAdmin(ModelAdmin):
    list_display = [
        "job",
        "bits_count",
        "hired_count",
        "invite_count",
        "proposal_count",
        "interview_count",
        "client_last_visit",
    ]
