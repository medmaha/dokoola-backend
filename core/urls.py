from django.urls import path

from . import views


urlpatterns = [
    path("health", views.health_check, name="health_1"),
    path("health/", views.health_check, name="health_2"),
    # path("waitlist/", views.waitlist, name="waitlist"),
    # path("api/categories/", views.CategoriesView.as_view(), name="categories"),
    # path("", views.index, name="index"),
]
