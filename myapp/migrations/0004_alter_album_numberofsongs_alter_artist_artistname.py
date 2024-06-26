# Generated by Django 5.0.3 on 2024-04-16 23:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_remove_artist_thumbnail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='numberOfSongs',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='artist',
            name='artistName',
            field=models.CharField(max_length=100, verbose_name='Artist Name'),
        ),
    ]
