from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
)
from rest_framework.response import Response

from .models import Notification
from .serializer import NotificationSerializer


class NotificationListAPIView(ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self, latest=False):
        user = self.request.user
        if latest:
            queryset = Notification.objects.filter(
                recipient=user, is_seen=False
            ).order_by("-created_at")
        else:
            queryset = Notification.objects.filter(recipient=user).order_by(
                "-created_at"
            )
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset("latest" in request.query_params)  # type: ignore
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True, context={"request": request})
        response = self.get_paginated_response(serializer.data)
        return response


class NotificationSeenAPIView(UpdateAPIView):

    def update(self, request, *args, **kwargs):
        user = request.user
        notification_ids = request.data

        Notification.objects.select_related().filter(
            recipient=user, id__in=notification_ids
        ).update(is_seen=True)

        return Response({}, status=200)


class NotificationReadAPIView(UpdateAPIView):

    def update(self, request, *args, **kwargs):
        user = request.user
        notification_ids = request.data

        Notification.objects.select_related().filter(
            recipient=user, id__in=notification_ids
        ).update(is_read=False)

        return Response({}, status=200)


class NotificationCheckAPIView(ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Notification.objects.filter(recipient=user, is_seen=False)[:3]
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
