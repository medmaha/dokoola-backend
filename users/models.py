from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext_lazy as _
from utilities.generator import id_generator

import random

from datetime import datetime, timedelta, tzinfo


class Manager(UserManager):
    use_in_migrations = True

    def create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class TZ_CLASS(tzinfo):
    def tzname(self, dt):
        return "GMT"

    def utcoffset(self, dt):
        return timedelta(0)

    def dst(self, dt):
        return timedelta(0)


def otp_expires_at():
    return datetime.now(tz=TZ_CLASS()) + timedelta(minutes=5)


class PaymentMethod(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    identifier = models.CharField(max_length=255)
    deleted = models.BooleanField(default=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def user(self) -> "User":
        return self.user_account  # type: ignore


class OTP(models.Model):
    user: "User | models.ForeignKey[None] " = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, null=True
    )
    identifier = models.CharField(null=True, max_length=255)
    code = models.CharField(max_length=8)
    is_sent = models.BooleanField(default=False)
    is_valid = models.BooleanField(default=False)
    expire_at = models.DateTimeField(default=otp_expires_at)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def generate_code(cls):
        return random.randrange(10000, 99999).__str__()


class User(AbstractUser):
    "The base User model of this application"
    _avt = "/img/default-avatar.jpg"

    id = models.CharField(
        primary_key=True, default=id_generator, editable=False, max_length=64
    )
    email = models.EmailField(max_length=100, unique=True)
    username = models.CharField(unique=True, max_length=32)
    slug = models.SlugField(max_length=100, default="", blank=True)
    gender = models.CharField(max_length=100, default="")
    avatar = models.CharField(default=_avt, blank=True, max_length=1000)
    last_name = models.CharField(default="", blank=True, max_length=100)
    first_name = models.CharField(default="", blank=True, max_length=100)

    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.SET_NULL,
        null=True,
        related_name="user_account",
    )

    is_active = models.BooleanField(default=False)
    is_client = models.BooleanField(default=False)
    is_freelancer = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    is_online = models.BooleanField(default=False)
    websocket_id = models.CharField(default="", blank=True, max_length=300)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = Manager()

    @property
    def name(self):
        return self.get_full_name()

    def __str__(self):
        return self.username

    def __repl__(self):
        return self.username

    @property
    def profile(self):
        if self.is_staff:
            return [self.staff_profile, "Staff"]  # type: ignore
        if self.is_client:
            return [self.client_profile, "Client"]  # type: ignore
        if self.is_freelancer:
            return [self.freelancer_profile, "Freelancer"]  # type: ignore
        return [None, ""]

    @classmethod
    def generate_otp(cls, user=None, identifier=None):

        code = OTP.generate_code()

        def save_otp(sent=False):
            OTP.objects.select_related("identifier").filter(
                identifier=identifier
            ).update(is_valid=False)
            OTP.objects.create(
                code=code, user=user, is_sent=sent, is_valid=True, identifier=identifier
            )

        return (code, save_otp)

    @classmethod
    def check_otp(cls, code, identifier):
        try:
            otp = OTP.objects.filter(
                code=code,
                is_valid=True,
                expire_at__gte=datetime.now(tz=TZ_CLASS()),
                identifier=identifier,
            )
            return otp.exists(), lambda: OTP.objects.filter(
                identifier=identifier
            ).update(is_valid=False)
        except OTP.DoesNotExist:
            return False, lambda: None
