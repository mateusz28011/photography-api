from accounts.serializers import UserSerializer
from rest_framework import serializers

from .models import Note, Order


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = "__all__"
        extra_kwargs = {"created": {"read_only": True}, "user": {"read_only": True}}


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "vendor", "client", "description", "cost"]
        extra_kwargs = {"vendor": {"required": True}, "client": {"required": True}}

    def validate(self, attrs):
        instance = Order(**attrs)
        instance.clean()
        return attrs


class OrderNestedSerializer(OrderSerializer):
    vendor = UserSerializer(read_only=True)
    client = UserSerializer(read_only=True)
    notes = NoteSerializer(read_only=True, many=True)

    class Meta(OrderSerializer.Meta):
        fields = OrderSerializer.Meta.fields + ["notes"]
