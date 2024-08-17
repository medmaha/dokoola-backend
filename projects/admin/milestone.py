from unfold.admin import ModelAdmin
from django.contrib import admin
from .. import models


@admin.register(models.Milestone)
class MilestoneModelAdmin(ModelAdmin):
    pass
