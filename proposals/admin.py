from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Proposal


@admin.register(Proposal)
class ActivityModelAdmin(ModelAdmin):
    list_display = [
        "job",
        "budget",
        "talent",
        "duration",
    ]
