from django.contrib import admin
from unfold.admin import ModelAdmin

from jobs import models


@admin.register(models.Pricing)
class PricingModelAdmin(ModelAdmin):
    pass
