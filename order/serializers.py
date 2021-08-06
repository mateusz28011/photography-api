from accounts.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Note, Order


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        exclude = ["order"]
        extra_kwargs = {"created": {"read_only": True}, "user": {"read_only": True}}


class OrderSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display")

    class Meta:
        model = Order
        fields = ["id", "vendor", "client", "description", "status", "status_display"]
        extra_kwargs = {"vendor": {"required": True}}

    def validate(self, attrs):
        if attrs["vendor"] == attrs["client"]:
            raise ValidationError({"vendor": "Vendor and client can not be equal."})
        if attrs["vendor"].is_vendor == False:
            raise ValidationError({"vendor": "This user is not vendor."})
        return attrs


class OrderNestedSerializer(OrderSerializer):
    vendor = UserSerializer(read_only=True)
    client = UserSerializer(read_only=True)
    notes = serializers.SerializerMethodField()
    # notes = NoteSerializer(read_only=True, many=True)

    class Meta(OrderSerializer.Meta):
        fields = OrderSerializer.Meta.fields + ["notes", "cost", "currency"]

    def get_notes(self, obj):
        notes = obj.note_set.all()
        return NoteSerializer(notes, many=True).data
