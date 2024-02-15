from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify

from utilities.generator import hex_generator
from .models import Activities, Job

@receiver(pre_save, sender=Job)
def create_activities(sender, instance:Job, **kwargs):
      if not instance.slug:
         instance.slug = slugify(f'{hex_generator(6)}') + '-' + slugify(instance.title[:16])

