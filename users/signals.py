from django.contrib.auth.hashers import is_password_usable, make_password
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import User


@receiver(post_save, sender=User)
def activate_superuser(sender, instance: User, created, **kwargs):
    if created:
        instance.is_active = True
        instance.save()


@receiver(pre_save, sender=User)
def encrypt_passwords(sender, instance: User, **kwargs):
    # if not instance.is_superuser and not instance.password.startswith("pbkdf2"):
    # instance.set_password(instance.password)
    # Check if the password is already hashed
    if instance.password and not is_password_usable(instance.password):
        # Replace the plain-text password with an encrypted version
        instance.password = make_password(instance.password)
    else:
        instance.password = ""
