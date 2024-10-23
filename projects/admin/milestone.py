from django.contrib import admin
from unfold.admin import ModelAdmin

from .. import models


@admin.register(models.Milestone)
class MilestoneModelAdmin(ModelAdmin):
    pass
