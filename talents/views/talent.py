from django.db import models, transaction
from django.utils import timezone
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from talents.models import Talent
from users.models.user import User
from users.serializer import UserWriteSerializer
from users.views.account.auth_token import GenerateToken
from utilities.generator import get_serializer_error_message

from ..search import TalentsSearchAPIView
from ..serializers import TalentReadSerializer, TalentWriteSerializer


class TalentAPIView(GenericAPIView):
    permission_classes = []
    serializer_class = TalentReadSerializer

    def get_serializer(self, *args, **kwargs):
        context = kwargs.get("context", {})
        r_type = context.get("r_type")

        if not r_type:
            r_type = self.request.query_params.get("r_type")
            context["r_type"] = str(r_type)
            kwargs["context"] = context

        return super().get_serializer(*args, **kwargs)

    def get(self, request, public_id=None):
        try:
            if public_id:
                if not request.user.is_authenticated:
                    return Response({"message": "Unauthorized Request"}, status=401)

                talent = Talent.objects.prefetch_related("user").get(
                    models.Q(public_id=public_id) | models.Q(user__username=public_id)
                )

                r_type = request.query_params.get("r_type") or "common"

                serializer = self.get_serializer(talent, context={"r_type": r_type})
                return Response(serializer.data, status=200)

            queryset = TalentsSearchAPIView.make_query(request).order_by("badge")
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(
                page, many=True, context={"retrieve": public_id is not None}
            )
            return self.get_paginated_response(serializer.data)

        except Talent.DoesNotExist:
            # TODO: log error
            return Response({"message": "Talent does not exist"}, status=404)

        except Exception as e:
            # TODO: log error
            return Response({"message": "Invalid request"}, status=500)

    def post(self, request, public_id=None):
        try:
            with transaction.atomic():
                user_serializer = UserWriteSerializer(data=request.data)
                talent_serializer = TalentWriteSerializer(data=request.data)

                _password = str(request.data.get("password", ""))

                if not _password:
                    return Response({"message": "Password is required"}, status=400)

                if len(_password) < 6:
                    return Response({"message": "Password is too short"}, status=400)

                if not user_serializer.is_valid():
                    error_msg = get_serializer_error_message(user_serializer.errors)
                    return Response({"message": error_msg}, status=400)

                if not talent_serializer.is_valid():
                    error_msg = get_serializer_error_message(talent_serializer.errors)
                    return Response({"message": error_msg}, status=400)

                # Save the new talent record with associated user
                _user: User = user_serializer.save(password=_password)
                _talent = talent_serializer.save(user=_user)

                # _user.set_password(_password)
                # _user.save()

                _serializer = self.get_serializer(_talent, context={"r_type": "detail"})
                return Response(_serializer.data, status=201)

        except Exception as e:
            # TODO: log error
            print("Error:", e)
            return Response({"message": "Invalid request"}, status=500)

    def put(self, request, public_id):
        try:
            talent = Talent.objects.get(public_id=public_id)

            assert talent.user == request.user, "403 Unauthorized user"

            talent_serializer = TalentWriteSerializer.merge_serialize(
                talent, request.data
            )
            if not talent_serializer.is_valid():
                msg = get_serializer_error_message(
                    talent_serializer.errors, "Invalid talent data"
                )
                # raised the same error as the serializer
                return Response({"message": msg}, status=400)

            user_serializer = UserWriteSerializer.merge_serialize(
                talent.user,
                request.data,
                metadata={"exclude": ("email", "password")},
            )
            if not user_serializer.is_valid():
                msg = get_serializer_error_message(
                    user_serializer.errors, "Invalid user data"
                )
                return Response({"message": msg}, status=400)

            current_username = request.user.username

            updated_user: User = user_serializer.save()
            updated_talent: Talent = talent_serializer.save()

            _serializer = TalentReadSerializer(
                updated_talent, context={"r_type": "detail"}
            )

            # Check to see of username of this user was updated
            if updated_user.username != current_username:
                # Generate a new token for this user's credentials
                token = GenerateToken().tokens(updated_user, init=True)
                return Response(
                    {
                        "tokens": token,
                        "message": "User updated successfully",
                        **_serializer.data,
                    },
                    status=200,
                )

            return Response(talent_serializer.data, status=200)

        except Talent.DoesNotExist:
            # TODO: log error
            return Response(
                {"message": "Error: User doesn't exist!"},
                status=404,
            )

        except AssertionError as e:
            return Response(
                {"message": str(e)},
                status=403,
            )

        except Exception as e:
            # TODO: log error
            return Response(
                {"message": "Error: Something went wrong!"},
                status=500,
            )

    def delete(self, request, public_id):
        """Performs a soft delete of a talent record"""
        try:
            with transaction.atomic():
                Talent.objects.get(public_id=public_id, user=request.user)
                Talent.objects.filter(public_id=public_id, user=request.user).update(
                    deleted_at=timezone.now()
                )
                return Response(
                    {"message": "Talent softly deleted successfully"}, status=200
                )

        except Talent.DoesNotExist:
            # TODO: log error
            return Response(
                {"message": "Error: talent doesn't exist!"},
                status=404,
            )

        except Exception as e:
            # TODO: log error
            return Response({"message": "Invalid request"}, status=500)
