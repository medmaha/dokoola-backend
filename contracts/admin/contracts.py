from unfold.admin import ModelAdmin
from django.contrib import admin
from .. import models


@admin.register(models.Contract)
class ContractModelAdmin(ModelAdmin):
    pass
