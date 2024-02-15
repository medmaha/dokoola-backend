from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView

from .serializer import NotificationSerializer
from .models import Notification


class NotificationListAPIView(ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Notification.objects.filter(recipient=user)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True, context={"request": request})
        response = self.get_paginated_response(serializer.data)
        return response


class NotificationCheckAPIView(RetrieveAPIView):
    def get_queryset(self):
        user = self.request.user
        queryset = Notification.objects.filter(recipient=user, is_seen=False)
        return queryset.exists()

    def retrieve(self, request, *args, **kwargs):
        queryset_exists = self.get_queryset()
        return Response({"new": queryset_exists})
