import os

from core.settings import BASE_DIR
from django.db.models.signals import post_delete, pre_delete
from django.dispatch import receiver

from .models import Album, Image


@receiver(pre_delete, sender=Image)
def image_pre_delete(sender, instance, *args, **kwargs):
    instance.image.delete()


@receiver(post_delete, sender=Album)
def album_post_delete(sender, instance, *args, **kwargs):
    path = f"{BASE_DIR}\\protected\\users\\user_{instance.creator.id}\\{instance.id}"
    if os.path.isdir(path):
        os.rmdir(path)
