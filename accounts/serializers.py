from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from .models import Profile, User


class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = [
            "id",
            "email",
            "password",
            "first_name",
            "last_name",
        ]


class UserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "join_date",
            "is_staff",
            "is_vendor",
        ]
        read_only_fields = [
            "email",
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
        extra_kwargs = {
            "portfolio": {"read_only": True},
            "owner": {"read_only": True},
            "avatar": {"read_only": False},
        }


class ProfileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ["payment_info", "portfolio", "owner"]


class ProfileNestedSerializer(ProfileSerializer):
    from album.serializers import AlbumSerializer

    portfolio = AlbumSerializer(read_only=True)
    owner = UserBasicInfoSerializer(read_only=True)
