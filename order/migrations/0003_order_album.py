# Generated by Django 3.2.5 on 2021-08-02 11:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('album', '0012_album_is_public'),
        ('order', '0002_auto_20210724_1750'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='album',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='album.album'),
        ),
    ]