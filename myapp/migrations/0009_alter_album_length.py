# Generated by Django 5.0.3 on 2024-04-21 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0008_album_averagestreams_album_totalstreams_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='length',
            field=models.DurationField(default=0),
        ),
    ]