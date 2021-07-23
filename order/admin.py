from django.contrib import admin

from .models import Note, Order

admin.site.register(Order)
admin.site.register(Note)
