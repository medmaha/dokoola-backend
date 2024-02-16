
from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver

from .models import User

@receiver(post_save, sender=User)
def activate_superuser(sender, instance:User, created, **kwargs):
    if created :
        instance.is_active = True
        instance.save()
        
@receiver(pre_save, sender=User)
def encrypt_passwords(sender, instance:User, **kwargs):
    if not instance.is_superuser:
        if not instance.password.startswith('pbkdf2'):
            instance.set_password(instance.password)
    