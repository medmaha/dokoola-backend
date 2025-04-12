import re

from django.contrib.auth.hashers import is_password_usable, make_password
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from clients.models import Client
from staffs.models import Staff
from talents.models.talent import Talent

from .models import User


@receiver(pre_save, sender=User)
def encrypt_passwords(sender, instance: User, **kwargs):

    if is_password_usable(instance.password):
        return instance

    password_hash_pattern = r"^pbkdf2_sha256\$.*"
    is_password_hashed = bool(re.match(password_hash_pattern, instance.password))

    if instance.password and not is_password_hashed:
        instance.password = make_password(instance.password)

    return instance


@receiver(post_save, sender=Talent)
def talent_profile(sender, instance: Talent, created, **kwargs):
    __update_user_public_id(instance.public_id, instance.user)


@receiver(post_save, sender=Client)
def client_profile(sender, instance: Client, created, **kwargs):

    __update_user_public_id(instance.public_id, instance.user)


@receiver(post_save, sender=Staff)
def staff_profile(sender, instance: Staff, created, **kwargs):
    __update_user_public_id(instance.public_id, instance.user)


def __update_user_public_id(public_id: str, user: User):
    if public_id and public_id != user.public_id:
        user.public_id = public_id
        User.objects.filter(pk=user.pk).bulk_update([user], fields=["public_id"])
