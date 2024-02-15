from django.urls import path

from . import views

urlpatterns = [
    path('', views.ClientListView.as_view(), name='clients'),
    path('<pk>',views.ClientListView.as_view(), name='client')
    ]
