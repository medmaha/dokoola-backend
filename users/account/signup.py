import random
import re, os, threading
from xmlrpc.client import Boolean
from django.core.mail import send_mail
from django.db import transaction
from django.template.loader import render_to_string
from src.settings.email import EMAIL_HOST_DOMAIN
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView, GenericAPIView

from staffs.models import Staff
from clients.models import Client
from clients.serializer import ClientUpdateSerializer
from freelancers.models import Freelancer
from freelancers.serializers import FreelancerUpdateSerializer
from users.models import User

from ..token import GenerateToken
from ..serializer import UserCreateSerializer, UserUpdateSerializer


class CheckEmailView(GenericAPIView):
    permission_classes = ()
    authentication_classes = ()

    def send_verification_code(self, email):
        code, save_otp = User.generate_otp(identifier=email)
        html = render_to_string("users/email_verification.html", context={"code": code})

        try:
            def mailer():
                try:
                    saved = save_otp(sent=False)
                    if not saved:
                        return 
                    response = send_mail(
                        "Email Verification",
                        f"Please use the following code to verify your email address: {code}", 
                        EMAIL_HOST_DOMAIN,
                        [email],
                        html_message=html,
                        fail_silently=True,
                    )
                    save_otp(sent=Boolean(response))
                except Exception as _:
                    pass 
            
            threading.Thread(target=mailer).start()
        except Exception as _:
            mailer()
        except:
            save_otp(False)

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        exists = User.objects.select_related("email").filter(email=email).exists()

        if not exists:
            self.send_verification_code(email)

        return Response(
            {
                "exists": exists,
                "message": (
                    "An account with this email already exist"
                    if exists
                    else "No account with this email"
                ),
            },
            status=400 if exists else 200,
        )


class ResendCodeView(GenericAPIView):
    permission_classes = ()
    authentication_classes = ()

    def resend_verification_code(self, email):
        code, save_otp = User.generate_otp(identifier=email)
        html = render_to_string("users/email_verification.html", context={"code": code})

        def mailer():
            try:
                saved = save_otp(sent=False)
                if not saved:
                    return 
                response = send_mail(
                    "Email Verification",
                    f"""
                        Please use the following code to verify your email address: {code}
                    """,
                    EMAIL_HOST_DOMAIN,
                    [email],
                    html_message=html,
                    fail_silently=True,
                )
                save_otp(sent=Boolean(response))
            except Exception as _:
                pass 
        try:
            threading.Thread(target=mailer).start()
        except Exception as _:
            mailer()
        except:
            pass

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        self.resend_verification_code(email)
        return Response(
            {
                "message": ("Successfully sent the code"),
            }
        )


class VerifyCodeView(GenericAPIView):
    permission_classes = ()
    authentication_classes = ()

    def verify_verification_code(self, code, email):
        return User.check_otp(code, email)

    def post(self, request, *args, **kwargs):
        code = request.data.get("code")
        email = request.data.get("email")
        verified, invalidate = self.verify_verification_code(code, email)


        print(request.data)
        if verified:
            invalidate()
            return Response(
                {
                    "verified": True,
                    "message": ("Successfully sent the code"),
                }
            )
        return Response(
            {
                "verified": False,
                "message": "Invalid verification code",
            },
            status=400,
        )


class SignUpView(APIView):
    permission_classes = ()

    def username_suffix(self, _suffix):
        suffix = random.randrange(10, 999)

        if str(suffix) == _suffix:
            return self.username_suffix(suffix)
        return str(suffix)

    def post(self, request, *args, **kwargs):
        data = request.data.copy()

        username = data.get("username")

        with transaction.atomic():
            while True:
                username_exists = User.objects.filter(username=username).exists()
                if username_exists:
                    _username = re.sub(r"[0-9]", "", username)
                    username = _username + self.username_suffix(
                        username[: len(username) - 3]
                    )
                else:
                    break

            data["username"] = username
            serializer = UserCreateSerializer(data=data)

            if serializer.is_valid():
                user: User = serializer.save()  # type: ignore
                user.is_active = False
                token_generator = GenerateToken()
                tokens = token_generator.tokens(user, init=True, context={"request": request})  # type: ignore
                user.set_password(data.get("password", "dokoola"))

                if user.is_staff:
                    Staff.objects.get_or_create(user=user)
                if user.is_client:
                    Client.objects.get_or_create(user=user)
                if user.is_freelancer:
                    Freelancer.objects.get_or_create(user=user)

                # TODO: send a welcome email to the user
                return Response(tokens, status=201)

            message = ""

            for error in serializer.errors.items():  # type: ignore
                field, text = error[0], error[1][0]

                if re.search(rf"{field}", text, re.IGNORECASE):
                    message = text.capitalize()
                    break

                message = field.capitalize() + ": " + text
                break

            return Response({"message": message}, status=400)


class SignupUserInformation(UpdateAPIView):

    def update(self, request, *args, **kwargs):
        user: User = request.user

        profile, _ = user.profile

        data = request.data.copy()

        if "avatar" in data and not len(data.get("avatar", "")):
            del data["avatar"]

        with transaction.atomic():
            if profile:
                username = data.get("username")
                username_exists = (
                    User.objects.select_related("id", "username")
                    .select_for_update()
                    .filter(username=username)
                    .exclude(id=user.id)
                    .exists()
                )

                if username_exists:
                    return Response(
                        {"message": "Sorry! this username already exist"}, status=400
                    )
                data["is_valid"] = True
                user_serializer = UserUpdateSerializer(instance=request.user, data=data)

                if user_serializer.is_valid():
                    user_serializer.save()
                else:
                    error_message = user_serializer.errors
                    return Response(dict(message=error_message), status=400)

                if isinstance(profile, Freelancer):
                    profile_serializer = FreelancerUpdateSerializer(
                        instance=profile, data=data
                    )
                    if profile_serializer.is_valid():
                        profile_serializer.save()

                        token_generator = GenerateToken()
                        tokens = token_generator.tokens(  # type: ignore
                            user, context={"request": request}
                        )
                        return Response(tokens, status=200)
                    return Response(
                        {"message": "Invalid values are passed to the payload"},
                        status=400,
                    )

                if isinstance(profile, Client):
                    profile_serializer = ClientUpdateSerializer(
                        instance=profile, data=data
                    )
                    if profile_serializer.is_valid():
                        profile_serializer.save()
                        token_generator = GenerateToken()
                        tokens = token_generator.tokens(  # type: ignore
                            user, context={"request": request}
                        )
                        return Response(tokens, status=200)
                    
                    return Response(
                        {"message": "Invalid values are passed to the payload"},
                        status=400,
                    )

        return Response({"message": "Request is forbidden/unauthorize"}, status=403)
