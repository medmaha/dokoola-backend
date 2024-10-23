from django.urls import path

from . import api_views, views

urlpatterns = [
    path("status", views.status, name="status_1"),
    path("status/", views.status, name="status_2"),
    path("health", views.health, name="health_1"),
    path("health/", views.health, name="health_2"),
    path("waitlist/", views.waitlist, name="waitlist"),
    # API
    path(
        "api/feedbacks/",
        api_views.FeedbackAPIView.as_view(),
        name="feedbacks",
    ),
    path(
        "api/categories/",
        api_views.CategoryAPIView.as_view(),
        name="categories",
    ),
    #
    path("", views.index, name="index"),
]
