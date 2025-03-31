from django.urls import path

from . import views

# pattern: /api/agent/*/**/
urlpatterns = [
    path("", views.index, name="index"),
    path("invalid-jobs/", views.invalidate_jobs, name="invalid_jobs"),
]
