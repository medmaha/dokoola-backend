from unfold.admin import ModelAdmin
from django.contrib import admin
from jobs import models


@admin.register(models.Pricing)
class PricingModelAdmin(ModelAdmin):
    pass
