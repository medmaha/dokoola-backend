from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext_lazy as _
from utilities.generator import id_generator

from typing import Any


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


class User(AbstractUser):
    "The base User model of this application"

    _avt = "/img/default-avatar.jpg"

    id = models.CharField(
        primary_key=True, default=id_generator, editable=False, max_length=64
    )
    email = models.EmailField(max_length=100, unique=True)
    username = models.CharField(unique=True, max_length=32)
    slug = models.SlugField(max_length=100, default="", blank=True)
    avatar = models.CharField(default=_avt, blank=True, max_length=1000)
    last_name = models.CharField(default="", blank=True, max_length=100)
    first_name = models.CharField(default="", blank=True, max_length=100)

    is_active = models.BooleanField(default=False)
    is_client = models.BooleanField(default=False)
    is_freelancer = models.BooleanField(default=False)

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
