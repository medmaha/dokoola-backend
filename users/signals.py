import re

from django.contrib.auth.hashers import is_password_usable, make_password
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import User


@receiver(pre_save, sender=User)
def encrypt_passwords(sender, instance: User, **kwargs):

    password_hash_pattern = r"^pbkdf2_sha256\$.*"
    is_password_hashed = bool(re.match(password_hash_pattern, instance.password))

    if instance.password and not is_password_hashed:
        instance.password = make_password(instance.password)
    return instance
