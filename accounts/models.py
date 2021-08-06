from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.files.images import get_image_dimensions
from django.db import models
from django.utils import timezone
from rest_framework.exceptions import ValidationError


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **other_fields):
        email = self.normalize_email(email)
        # if User.objects.filter(email=email).exists():
        #     raise ValidationError({"email": "Email exists"})
        user = self.model(email=email, **other_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **other_fields):
        other_fields.setdefault("is_staff", True)
        other_fields.setdefault("is_superuser", True)
        other_fields.setdefault("is_active", True)
        return self.create_user(email, password, **other_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    join_date = models.DateTimeField(default=timezone.now)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_vendor = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return self.email


def validate_image(image):
    w, h = get_image_dimensions(image)
    if w > 500 or h > 500:
        raise ValidationError({"avatar": "Maximum avatar size is 500x500 px."})


def user_directory_path(instance, filename):
    return f"profiles/user_{instance.owner.id}/avatar/{filename}"


class Profile(models.Model):
    name = models.CharField(max_length=100)
    avatar = models.ImageField(
        upload_to=user_directory_path, default="default/avatar.png", blank=True, validators=[validate_image]
    )
    description = models.TextField()
    payment_info = models.TextField()
    portfolio = models.OneToOneField("album.Album", on_delete=models.PROTECT, blank=True)
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
