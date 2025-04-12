from django.db import transaction
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.services.after.main import AfterResponseService
from users.models import User
from utilities.generator import get_serializer_error_message
from utilities.time import utc_datetime

from .models import Message, Thread
from .serializer import (
    MessagingCreateSerializer,
    MessagingListSerializer,
    ThreadListSerializer,
)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def latest_thread(request):
    user = request.user
    thread = Thread.objects.filter(owner=user).latest()

    serializer = ThreadListSerializer(thread, many=False, context={"request": request})

    return Response(serializer.data, status=200)


class ThreadDeleteAPIView(DestroyAPIView):
    def get_queryset(self, id: str):
        thread = Thread.objects.filter(unique_id=id, owner=self.request.user).first()
        deleted = False

        if thread:
            thread.delete()
            deleted = True

        return deleted

    def destroy(self, request, *args, **kwargs):
        id = request.data.get("id")

        if not id:
            return Response(
                {"message": "This request is forbidden/prohibited"},
                status=403,
            )

        if self.get_queryset(id):
            return Response({}, status=200)
        return Response({"message": "This request is forbidden/prohibited"}, status=403)


class ThreadListAPIView(ListAPIView):
    serializer_class = ThreadListSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = (
            Thread.objects.filter(owner=user, messaging__gt=0)
            .order_by("-updated_at")
            .distinct()
        )
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True, context={"request": request})
        response = self.get_paginated_response(serializer.data)
        return response


class ThreadSearchAPIView(ListAPIView):
    serializer_class = ThreadListSerializer

    def get_queryset(self, search_params: dict):
        user = self.request.user
        query = search_params.get("q")

        if query:
            queryset = Thread.objects.filter(
                Q(recipient__public_id__icontains=query)
                | Q(recipient__first_name__icontains=query)
                | Q(recipient__last_name__icontains=query),
                owner=user,
            )
            return queryset

        return []

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset(request.query_params)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True, context={"request": request})
        response = self.get_paginated_response(serializer.data)
        return response


class ThreadMessagesAPIView(ListAPIView):
    serializer_class = MessagingListSerializer

    def get_queryset(self, query_params):
        user = self.request.user
        thread_unique_id = query_params.get("id", "")

        if isinstance(thread_unique_id, list):
            thread_unique_id = thread_unique_id[0]

        thread = Thread.objects.filter(owner=user, unique_id=thread_unique_id).first()

        if thread:
            queryset = thread.messaging.filter().order_by("created_at")
            return queryset
        return

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset(request.query_params)

        if not queryset:
            return Response(status=403)

        page = self.paginate_queryset(queryset)

        serializer = self.get_serializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)  # type:ignore


class MessagingCreateAPIView(CreateAPIView):
    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                recipient_public_id: str = request.data.get("recipient")
                if not recipient_public_id:
                    return Response({"message": "This request is invalid"}, status=400)

                [profile, profile_type] = User.get_profile_by_username_or_public_id(
                    recipient_public_id
                )

                if not profile:
                    return Response({"message": "This request is invalid"}, status=400)

                if profile.public_id == request.user.public_id:
                    return Response({"message": "This request is invalid"}, status=400)

                sender: User = request.user
                recipient: User = profile.user

                sender_thread, created = Thread.objects.get_or_create(
                    owner=sender, recipient=recipient
                )
                recipient_thread = Thread.objects.get_or_create(
                    owner=recipient, recipient=sender
                )[0]

                unique_id = (
                    sender.public_id.replace("_", "")
                    + "_"
                    + recipient.public_id.replace("_", "")
                )

                save_sender_thread = False
                save_recipient_thread = False

                if not sender_thread.unique_id:
                    save_sender_thread = True
                    sender_thread.unique_id = unique_id
                if not recipient_thread.unique_id:
                    save_recipient_thread = True
                    recipient_thread.unique_id = unique_id

                message_data = {}
                message_data["sender"] = sender
                message_data["recipient"] = recipient
                message_data["content"] = request.data.get("content", "")

                serializer = MessagingCreateSerializer(
                    data=message_data, context={"request": request}
                )

                if not created:
                    save_sender_thread = True
                    save_recipient_thread = True
                    sender_thread.updated_at = utc_datetime(add_minutes=1)
                    recipient_thread.updated_at = utc_datetime(add_minutes=1)

                if not serializer.is_valid():
                    error_message = get_serializer_error_message(serializer.errors)
                    return Response({"message": error_message}, status=400)

                new_message = Message.objects.create(**message_data)

                sender_thread.messaging.add(new_message)
                recipient_thread.messaging.add(new_message)

                serializer = MessagingListSerializer(new_message)
                response = {"chat": serializer.data}

                if created:
                    t_serializer = ThreadListSerializer(
                        sender_thread, context={"request": request}
                    )
                    response["thread"] = t_serializer.data

                def update_threads_info():
                    if save_sender_thread and save_recipient_thread:
                        updated_fields = ["updated_at"]
                        if created:
                            updated_fields.append("unique_id")

                        Thread.objects.filter(
                            Q(owner=sender, recipient=recipient)
                            | Q(owner=recipient, recipient=sender)
                        ).bulk_update(
                            [sender_thread, recipient_thread], fields=updated_fields
                        )

                    elif save_sender_thread:
                        recipient_thread.save()
                    elif save_sender_thread:
                        sender_thread.save()

                AfterResponseService.schedule_after(update_threads_info)

                return Response(response, status=201)

        except Exception as e:
            # TODO: log error
            return Response({"message": "Internal Server Error"}, status=500)
