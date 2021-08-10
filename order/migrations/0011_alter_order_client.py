# Generated by Django 3.2.5 on 2021-08-09 10:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('order', '0010_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='client',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, related_name='client', to=settings.AUTH_USER_MODEL),
        ),
    ]