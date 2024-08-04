from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("waitlist/", views.waitlist, name="waitlist"),
    path("api/categories/", views.CategoriesView.as_view(), name="categories"),
]
