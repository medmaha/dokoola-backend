from typing import Any, Literal, Union

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from clients.models import Client
from staffs.models import Staff
from talents.models import Talent


class User(AbstractUser):
    "The base User model of this application"

    email = models.EmailField(max_length=100, unique=True, db_index=True)
    username = models.CharField(unique=True, max_length=32, db_index=True)
    public_id = models.CharField(max_length=100, default="", blank=True, db_index=True)

    avatar = models.CharField(null=True, blank=True, max_length=1000)

    first_name = models.CharField(default="", blank=True, max_length=100)
    last_name = models.CharField(default="", blank=True, max_length=100)

    gender = models.CharField(max_length=100, default="", blank=True, db_index=True)

    is_active = models.BooleanField(default=False)
    is_client = models.BooleanField(default=False)
    is_talent = models.BooleanField(default=False)

    email_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    DEFAULT_PASSWORD = "%!dokoola#"

    # Personal info
    phone = models.CharField(max_length=50, default="", blank=True)
    phone_code = models.CharField(max_length=10, default="", blank=True)
    country = models.CharField(
        default="",
        blank=True,
        max_length=100,
        null=True,
    )
    country_code = models.CharField(max_length=10, default="", blank=True)
    state = models.CharField(max_length=50, default="", blank=True, null=True)
    district = models.CharField(max_length=50, default="", blank=True, null=True)
    city = models.CharField(default="", blank=True, max_length=100, null=True)
    zip_code = models.CharField(max_length=20, default="00000", blank=True, null=True)

    def __str__(self):
        return self.email

    @property
    def name(self):
        return self.get_full_name()

    @property
    def profile(self):
        return self.get_profile()

    def get_profile(self) -> "ProfileType":
        if self.is_client:
            return (self.client_profile, "Client")  # type: ignore
        if self.is_talent:
            return (self.talent_profile, "Talent")  # type: ignore
        return (self.staff_profile, "Staff")  # type: ignore

    @property
    def account_type(self):
        if self.is_staff:
            return "Staff"
        if self.is_client:
            return "Client"
        if self.is_talent:
            return "Talent"
        return "User"

    def get_address(self):
        """Returns the client's address in a dictionary format"""
        return {
            "zip_code": self.zip_code,
            "country": self.country,
            "country_code": self.country_code,
            "phone_code": self.phone_code,
            "state": self.state,
            "district": self.district,
            "city": self.city,
        }

    def get_location(self):
        sub = self.city or self.state
        if sub:
            return f"{self.country} | {sub}"
        return self.country

    def get_personal_info(self):
        return {
            "phone": self.phone,
            "phone_code": self.phone_code,
            "country": self.country,
            "country_code": self.country_code,
            "state": self.state,
            "district": self.district,
            "city": self.city,
            "zip_code": self.zip_code,
        }

    @classmethod
    def get_profile_by_username_or_public_id(cls, public_id: str):
        if public_id.lower().startswith(Staff.PUBLIC_ID_PREFIX.lower()):
            profile = Staff
        elif public_id.lower().startswith(Client.PUBLIC_ID_PREFIX.lower()):
            profile = Client
        elif public_id.lower().startswith(Talent.PUBLIC_ID_PREFIX.lower()):
            profile = Talent
        else:
            profile = None

        if not profile:
            user = (
                User.objects.only(
                    "is_talent", "is_client", "is_staff", "id", "username"
                )
                .filter(username=public_id)
                .first()
            )
            if not user:
                return [None, ""]
            profile, profile_type = user.profile
            return [profile, profile_type]

        _profile = profile.objects.filter(public_id=public_id).first()
        return [_profile, profile.__name__ if _profile else ""]


ProfileType = Union[
    tuple[Staff, Literal["Staff"]],
    tuple[Client, Literal["Client"]],
    tuple[Talent, Literal["Talent"]],
]
