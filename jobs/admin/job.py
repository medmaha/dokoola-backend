from unfold.admin import ModelAdmin
from django.contrib import admin
from jobs import models


@admin.register(models.Job)
class JobModelAdmin(ModelAdmin):
    pass
