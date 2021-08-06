from album.models import Album
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Profile


@receiver(pre_save, sender=Profile)
def profile_pre_save(sender, instance, *args, **kwargs):
    if instance._state.adding:
        portfolio = Album.objects.create(name="Portfolio", creator=instance.owner, is_public=True)
        instance.portfolio = portfolio


@receiver(post_save, sender=Profile)
def profile_post_save(sender, instance, created, *args, **kwargs):
    if created == True:
        user = instance.owner
        user.is_vendor = True
        user.save()
