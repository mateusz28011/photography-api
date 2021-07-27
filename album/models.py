from accounts.models import User
from core.settings import BASE_DIR
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.utils import timezone

upload_storage = FileSystemStorage(location=settings.SENDFILE_ROOT, base_url="/protected")


def user_directory_path(instance, filename):
    return f"users/user_{instance.author.id}/{instance.album.id}/{filename}"


class Album(models.Model):
    name = models.CharField(max_length=100)
    creator = models.ForeignKey(User, related_name="creator", on_delete=models.PROTECT)
    allowed_users = models.ManyToManyField(User, blank=True)
    parent_album = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)


class Image(models.Model):
    height = models.PositiveIntegerField(null=True, blank=True)
    width = models.PositiveIntegerField(null=True, blank=True)
    image = models.ImageField(
        upload_to=user_directory_path, storage=upload_storage, height_field="height", width_field="width"
    )
    # image = models.ImageField(upload_to=user_directory_path, height_field="height", width_field="width")
    # title = models.CharField(max_length=250)
    # alt = models.TextField(null=True)
    # slug = models.SlugField(max_length=250, unique_for_date="created")
    created = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
