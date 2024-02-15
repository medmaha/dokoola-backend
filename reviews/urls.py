from django.urls import path

from . import views

urlpatterns = [
    path('', views.ReviewsListView.as_view(), name='reviews')
]