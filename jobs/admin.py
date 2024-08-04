from django.contrib import admin

from .models import Activities, Job, Pricing

from unfold.admin import ModelAdmin
from django.contrib import admin
from . import models

@admin.register(models.Job)
class JobAdminClass(ModelAdmin):
    pass
@admin.register(models.Pricing)
class PricingAdminClass(ModelAdmin):
    pass
@admin.register(models.Activities)
class ActivitiesAdminClass(ModelAdmin):
    pass