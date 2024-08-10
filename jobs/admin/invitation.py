from unfold.admin import ModelAdmin
from django.contrib import admin
from jobs import models


@admin.register(models.Invitation)
class InvitationModelAdmin(ModelAdmin):
    pass
