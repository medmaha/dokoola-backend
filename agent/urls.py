

from django.urls import path
from . import views


# pattern: /api/agent/*/**/
urlpatterns = [
    path("", views.index, name="index"),
]

