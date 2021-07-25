from accounts.models import User
from django.db import models
from django.utils import timezone
from rest_framework.serializers import ValidationError


class Order(models.Model):
    description = models.TextField()
    cost = models.FloatField(null=True, blank=True)
    vendor = models.ForeignKey(User, related_name="vendor", on_delete=models.PROTECT)
    client = models.ForeignKey(User, related_name="client", on_delete=models.PROTECT)
    # album = models.ForeignKey(Album, on_delete=models.SET_NULL, null=True, blank=True)
    # payment = models.ForeignKey( Payment, on_delete=models.SET_NULL, null=True,blank=True)
    # notes = models.ManyToManyField(Note, blank=True)

    def clean(self):
        if self.vendor == self.client:
            raise ValidationError({"vendor": "Vendor and client can not be equal."})


class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    note = models.TextField()
    created = models.DateTimeField(default=timezone.now)
