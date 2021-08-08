from accounts.serializers import UserSerializer
from album.serializers import AlbumSerializer
from django.http import request
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Note, Order


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        exclude = ["order"]
        extra_kwargs = {"created": {"read_only": True}, "user": {"read_only": True}}


class OrderSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    album = AlbumSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ["id", "vendor", "client", "description", "status", "status_display", "album"]
        extra_kwargs = {"vendor": {"required": True}}

    def validate(self, attrs):
        if attrs["vendor"] == attrs["client"]:
            raise ValidationError({"vendor": "Vendor and client can not be equal."})
        if attrs["vendor"].is_vendor == False:
            raise ValidationError({"vendor": "This user is not vendor."})
        return attrs


class OrderUpdateSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Order
        fields = ["id", "album", "cost", "currency", "status", "status_display"]

    def validate(self, attrs):
        current_status = self.instance.status
        request = self.context["request"]
        if "status" in attrs:
            new_status = attrs["status"]
            if self.instance.status in [0, 1, 6]:
                raise ValidationError(
                    {"status": 'You cannot change order status when is is "Canceled", "Rejected" or "Finished".'}
                )
            if request.user == self.instance.client:
                if new_status != 0 or current_status != 2:
                    raise ValidationError(
                        {
                            "status": 'You can only set status to "Canceled" when order\'s status is "Waiting for acceptance"'
                        }
                    )
            if request.user == self.instance.vendor:
                if new_status == 4 and self.instance.cost == None and ("cost" not in attrs):
                    raise ValidationError(
                        {"status": 'You can only set status to "Waiting for payment" when cost in order is set!'}
                    )
                if current_status == 2 and new_status not in [1, 3]:
                    raise ValidationError(
                        {
                            "status": 'You can only set status to "Canceled" or "Accepted" when order\'s status is "Waiting for acceptance"'
                        }
                    )
                if current_status == 3 and new_status not in [0, 4, 6]:
                    raise ValidationError(
                        {
                            "status": 'You can only set status to "Canceled", "Waiting for payment" or "Finished" when order\'s status is "Accepted"'
                        }
                    )
                if current_status == 4 and new_status not in [0, 5, 6]:
                    raise ValidationError(
                        {
                            "status": 'You can only set status to  "Canceled", "Payment received" or "Finished" when order\'s status is "Waiting for payment"'
                        }
                    )
                if current_status == 5 and new_status not in [0, 6]:
                    raise ValidationError(
                        {
                            "status": 'You can only set status to  "Canceled" or "Finished" when order\'s status is "Payment received"'
                        }
                    )
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
