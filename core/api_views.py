from rest_framework import serializers
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from core.models import Category, Feedback, Waitlist
from utilities.generator import get_serializer_error_message
from utilities.privacy import mask_email


# Categories ---------------------------------------------------------------------
class WaitlistSerializer(serializers.ModelSerializer):

    email = serializers.SerializerMethodField()

    class Meta:
        model = Waitlist
        fields = ["name", "email", "created_at", "updated_at"]

    def get_email(self, instance: Waitlist):
        return mask_email(instance.email)


class WaitlistAPIView(GenericAPIView):
    permission_classes = []
    serializer_class = WaitlistSerializer

    def get_queryset(self):
        queryset = Waitlist.objects.filter()
        return queryset

    def post(self, request):
        _message = None
        _status = 201

        name = request.data.get("name", "")
        email = request.data.get("email")

        serializer = None

        try:
            Waitlist.objects.filter().delete()
            subscriber = Waitlist.objects.get(email=email)
            _message = "You are already in our waitlist, Thank You!"
            _status = 200

            # Try to update the their name instead
            if name and subscriber.name.lower().strip() != name.lower().strip():
                subscriber.name = name
                subscriber.save()
                subscriber.refresh_from_db()

            serializer = WaitlistSerializer(instance=subscriber)

        except Waitlist.DoesNotExist:
            subscriber = Waitlist(name=name, email=email)
            _message = "Thank you for joining our waiting list"
            subscriber.save()
            serializer = WaitlistSerializer(instance=subscriber)

        except Exception as e:
            _status = 400
            _message = str(e)

        data = {
            "message": _message,
        }

        if serializer:
            data.update(dict(serializer.data))

        return Response(
            data,
            status=_status,
        )


class CategorySerializer(serializers.ModelSerializer):

    parent = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["slug", "name", "image_url", "description", "parent"]

    def get_parent(self, instance: Category):
        if not instance.parent:
            return None

        return {
            "slug": instance.parent.slug,
            "name": instance.parent.name,
            "image_url": instance.parent.image_url,
        }


class CategoryAPIView(GenericAPIView):
    permission_classes = []
    serializer_class = CategorySerializer

    def get_queryset(self, query_params):
        child = query_params.get("child", None)
        parent__isnull = True if child is None else bool(child) == False
        categories = Category.objects.filter(
            disabled=False, is_agent=False, parent__isnull=parent__isnull
        )
        return categories

    def get(self, request):
        # ids = set()
        # slugs = set()
        # for _c in Category.objects.all():
        #     if _c.name not in slugs:
        #         ids.add(_c.id)
        #         slugs.add(_c.name)
        # Category.objects.exclude(id__in=ids).delete()

        categories = self.get_queryset(request.query_params)
        serializers = self.get_serializer(categories, many=True)
        categories = serializers.data

        response = Response(categories, status=200)
        return response


# Feedbacks ----=-----------------------------------------------------------------
class FeedbackCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ["message", "author_name", "author_email", "rating"]


class FeedbackAPIView(GenericAPIView):
    permission_classes = []
    serializer_class = FeedbackCreateSerializer

    def get_serializer_class(self):
        class Serializer(serializers.ModelSerializer):
            class Meta:
                model = Feedback
                fields = [
                    "author_name",
                    "author_email",
                    "rating",
                    "likes_count",
                    "message",
                    "created_at",
                ]

        return Serializer

    def get(self, request):
        feedbacks = Feedback.objects.filter(blacklisted=False).order_by(
            "-rating", "-created_at"
        )[:3]

        serializers = self.get_serializer(feedbacks, many=True)
        feedbacks = serializers.data

        response = Response(feedbacks, status=200)
        return response

    def post(self, request):
        data = request.data.copy()

        early_return = False

        # If both author_name and author_email are not provided
        if (
            not data.get("author_name")
            and not data.get("author_email")
            and not data.get("rating")
        ):
            early_return = True

        # If message and rating are not provided
        if not data.get("message") and not data.get("rating"):
            early_return = True

        if early_return:
            return Response({"id": 10_0001}, status=200)

        feedback = self.get_serializer(data=data)
        if feedback.is_valid():
            instance = feedback.save()
            return Response({"id": instance.pk, "ok": True}, status=200)
        else:
            error_message = get_serializer_error_message(feedback.errors)
            return Response({"message": error_message}, status=400)
