# Generated by Django 3.2.5 on 2021-11-05 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('album', '0017_alter_image_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='title',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]