from djoser.serializers import UserCreateSerializer

from .models import User


class UserSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ("id", "email", "password", "first_name", "last_name", "join_date")


# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ["id", "email", "password", "first_name", "last_name", "join_date"]
#         extra_kwargs = {"password": {"write_only": True}}

#     def create(self, validated_data):
#         user = User.objects.create_user(**validated_data)
#         return user
