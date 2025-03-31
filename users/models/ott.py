import random

from django.db import models
from django.utils import timezone


class OTT(models.Model):
    """One Time Token for user verification"""

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, null=True)
    identifier = models.CharField(null=True, max_length=255)
    code = models.CharField(max_length=8)
    is_sent = models.BooleanField(default=False)
    is_valid = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    expire_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class OTTProxy(OTT):
    class Meta:
        proxy = True

    @classmethod
    def generate_ott(cls, identifier: str, user=None):
        """Generate a new OTT object. Note that this is not saved yet"""

        ott = OTT()
        ott.user = user
        ott.identifier = identifier
        ott.code = cls.generate_code()
        ott.expire_at = timezone.now() + timezone.timedelta(minutes=10)

        # Set all other OTTs to invalid
        OTT.objects.select_related().filter(identifier=identifier).update(
            is_valid=False
        )

        ott.save()
        return ott

    @classmethod
    def validate_ott(cls, identifier: str, code: str):
        return cls.objects.filter(identifier=identifier, code=code).exists()

    @classmethod
    def validate_verified_ott(cls, identifier: str):
        one_month_ago = timezone.now() - timezone.timedelta(weeks=4)
        return cls.objects.filter(
            identifier=identifier,
            is_valid=False,
            verified=True,
            updated_at__gte=one_month_ago,
        ).exists()

    @classmethod
    def generate_code(cls):
        return random.randrange(10000, 99999).__str__()

    @classmethod
    def invalidate_ott(cls, identifier: str, verified=True):
        cls.objects.filter(identifier=identifier).update(
            is_valid=False, verified=verified
        )
