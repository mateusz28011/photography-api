# Generated by Django 3.2.5 on 2021-07-29 15:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('album', '0011_alter_album_parent_album'),
        ('accounts', '0005_auto_20210729_1511'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='portfolio',
            field=models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, to='album.album'),
        ),
    ]
