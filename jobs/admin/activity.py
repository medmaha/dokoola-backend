from django.contrib import admin
from unfold.admin import ModelAdmin

from jobs import models


@admin.register(models.Activities)
class ActivityModelAdmin(ModelAdmin):
    pass
