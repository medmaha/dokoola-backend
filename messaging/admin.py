from django.contrib import admin

from .models import Message, Thread

# Register your models here.


admin.site.register(Thread)
admin.site.register(Message)
