# Generated by Django 3.2.5 on 2021-08-03 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0005_auto_20210802_1515'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('0', 'Canceled'), ('1', 'Waiting for acceptance'), ('2', 'Accepted'), ('3', 'Waiting for payment'), ('4', 'Payment received'), ('5', 'Finished')], default=1, max_length=1),
        ),
    ]
