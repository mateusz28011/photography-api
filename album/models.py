from accounts.models import User
from core.storage_backends import PrivateMediaStorage
from django.db import models
from django.utils import timezone
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill


def user_directory_path(instance, filename):
    return f"users/user_{instance.author.id}/{instance.album.id}/{filename}"


class Album(models.Model):
    name = models.CharField(max_length=100)
    creator = models.ForeignKey(User, related_name="creator", on_delete=models.PROTECT)
    allowed_users = models.ManyToManyField(User, blank=True)
    parent_album = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    created = models.DateTimeField(default=timezone.now)
    is_public = models.BooleanField(default=False)


class Image(models.Model):
    height = models.PositiveIntegerField(null=True, blank=True)
    width = models.PositiveIntegerField(null=True, blank=True)
    image = models.ImageField(
        upload_to=user_directory_path,
        storage=PrivateMediaStorage,
        height_field="height",
        width_field="width",
    )
    image_thumbnail = ImageSpecField(
        source="image",
        processors=[ResizeToFill(300, 200)],
        format="JPEG",
        options={"quality": 80},
    )
    title = models.CharField(max_length=100)
    created = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
