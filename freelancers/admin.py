
from unfold.admin import ModelAdmin
from django.contrib import admin
from . import models

@admin.register(models.Freelancer)
class FreelancerAdminClass(ModelAdmin):
    search_fields = ( 'phone', "country", "state", "district", 'website')
    list_display = ('name', "email", "badge", 'pricing', 'phone')