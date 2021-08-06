import os

from core.settings import BASE_DIR
from django.db.models.signals import post_delete, pre_delete, pre_save
from django.dispatch import receiver

from .models import Album, Image


@receiver(pre_save, sender=Image)
def image_pre_save(sender, instance, *args, **kwargs):
    if instance._state.adding:
        filename_with_extenstion = os.path.split(instance.image.name)[1]
        filename = filename_with_extenstion.split(".")[0]
        if len(filename) > 100:
            filename = filename[:100]
        instance.title = filename


@receiver(pre_delete, sender=Image)
def image_pre_delete(sender, instance, *args, **kwargs):
    instance.image.delete()


@receiver(post_delete, sender=Album)
def album_post_delete(sender, instance, *args, **kwargs):
    path = f"{BASE_DIR}\\protected\\users\\user_{instance.creator.id}\\{instance.id}"
    if os.path.isdir(path):
        os.rmdir(path)
