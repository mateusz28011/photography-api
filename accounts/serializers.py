from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from .models import Profile, User


class UserSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = [
            "id",
            "email",
            "password",
            "first_name",
            "last_name",
            "join_date",
            "is_staff",
            "is_vendor",
        ]


class UserBasicInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name"]


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"
        extra_kwargs = {"portofilo": {"read_only": True}, "owner": {"read_only": True}}


class ProfileNestedSerializer(ProfileSerializer):
    from album.serializers import AlbumSerializer

    portfolio = AlbumSerializer(read_only=True)
    owner = UserBasicInfoSerializer(read_only=True)
