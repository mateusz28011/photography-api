import os

from accounts.serializers import UserBasicInfoSerializer, UserSerializer
from core.settings import BASE_DIR
from rest_framework import serializers
from rest_framework.reverse import reverse

from .models import Album, Image


class AlbumSmallSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Album
        fields = ["id", "name", "url"]

    def get_url(self, obj):
        return reverse("album-detail", args=[obj.id], request=self.context["request"])


class AlbumSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    child_albums = serializers.SerializerMethodField()
    parent_album = AlbumSmallSerializer(read_only=True)
    creator = UserBasicInfoSerializer(read_only=True)
    allowed_users = UserBasicInfoSerializer(many=True, read_only=True)

    class Meta:
        model = Album
        fields = "__all__"
        extra_kwargs = {"created": {"read_only": True}, "allowed_users": {"read_only": True}}

    def get_images(self, obj):
        images = Image.objects.filter(album=obj)
        return ImageSerializer(images, many=True, context={"request": self.context["request"]}).data

    def get_child_albums(self, obj):
        albums = Album.objects.filter(parent_album=obj)
        return AlbumSmallSerializer(albums, many=True, context={"request": self.context["request"]}).data


class ImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Image
        exclude = ["image", "album"]
        extra_kwargs = {"created": {"read_only": True}}

    def get_url(self, obj):
        return reverse("image-detail", args=[obj.id], request=self.context["request"])
