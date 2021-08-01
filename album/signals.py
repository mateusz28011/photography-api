from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import Album, Image


@receiver(pre_delete, sender=Image)
def image_pre_delete(sender, instance, *args, **kwargs):
    instance.image.delete()
