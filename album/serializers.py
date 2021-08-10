from accounts.serializers import UserBasicInfoSerializer
from core.settings import BASE_DIR
from rest_framework import serializers
from rest_framework.reverse import reverse

from .models import Album, Image


class AlbumListSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    creator = UserBasicInfoSerializer(read_only=True)

    class Meta:
        model = Album
        fields = ["id", "creator", "name", "url", "is_public", "created"]

    def get_url(self, obj):
        return reverse("album-detail", args=[obj.id], request=self.context["request"])


class AlbumCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = ["id", "name", "parent_album", "is_public"]


class AlbumSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    child_albums = serializers.SerializerMethodField()
    parent_album = AlbumListSerializer(read_only=True)
    creator = UserBasicInfoSerializer(read_only=True)
    allowed_users = UserBasicInfoSerializer(many=True, read_only=True)

    class Meta:
        model = Album
        fields = "__all__"
        read_only_fields = ["created", "allowed_users"]

    def get_images(self, obj):
        images = obj.image_set.all()
        return ImageSerializer(images, many=True, context={"request": self.context["request"]}).data

    def get_child_albums(self, obj):
        albums = obj.album_set.all()
        return AlbumListSerializer(albums, many=True, context={"request": self.context["request"]}).data


class ImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Image
        exclude = ["image", "album"]

    def get_url(self, obj):
        request = self.context["request"]
        album_id = request.parser_context["kwargs"]["pk"]
        return reverse("album-images-detail", args=[album_id, obj.id], request=request)


class ImageUploadSerializer(ImageSerializer):
    class Meta(ImageSerializer.Meta):
        fields = ["image"]
        exclude = None


class ImageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ["id", "title"]
