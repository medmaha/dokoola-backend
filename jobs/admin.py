from django.contrib import admin

from .models import Activities, Job, Pricing

# Register your models here.
admin.site.register(Job)
admin.site.register(Pricing)
admin.site.register(Activities)