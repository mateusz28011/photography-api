# Generated by Django 3.2.5 on 2021-08-01 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('album', '0011_alter_album_parent_album'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='is_public',
            field=models.BooleanField(default=False),
        ),
    ]
