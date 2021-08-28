from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer
from django.db import transaction
from rest_framework import serializers

from .models import Profile, User


class CustomLoginSerializer(LoginSerializer):
    username = None
    email = serializers.EmailField(required=True)


class CustomRegisterSerializer(RegisterSerializer):
    username = None
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)

    # Define transaction.atomic to rollback the save operation in case of error
    @transaction.atomic
    def save(self, request):
        user = super().save(request)
        user.first_name = self.data.get("first_name")
        user.last_name = self.data.get("last_name")
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
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
            "created": {"read_only": True},
            "avatar": {"read_only": False},
        }


class ProfileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ["payment_info", "portfolio", "owner"]


class ProfileNestedSerializer(ProfileSerializer):
    owner = UserBasicInfoSerializer(read_only=True)
