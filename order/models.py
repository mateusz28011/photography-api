from accounts.models import User
from album.models import Album
from django.db import models
from django.utils import timezone
from rest_framework.serializers import ValidationError


class Order(models.Model):
    CURRENCIES = [("PLN", "Polish Zloty"), ("EUR", "Euro"), ("USD", "United States Dollar")]
    STATUSES = [
        ("0", "Canceled"),
        ("1", "Waiting for acceptance"),
        ("2", "Accepted"),
        ("3", "Waiting for payment"),
        ("4", "Payment received"),
        ("5", "Finished"),
    ]
    description = models.TextField()
    status = models.CharField(max_length=1, choices=STATUSES, default=1)
    cost = models.FloatField(null=True, blank=True)
    currency = models.CharField(max_length=3, choices=CURRENCIES, default="EUR")
    vendor = models.ForeignKey(User, related_name="vendor", on_delete=models.PROTECT)
    client = models.ForeignKey(User, related_name="client", on_delete=models.PROTECT)
    album = models.ForeignKey(Album, on_delete=models.SET_NULL, null=True, blank=True)


class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    note = models.TextField()
    created = models.DateTimeField(default=timezone.now)
