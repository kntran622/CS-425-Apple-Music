# Generated by Django 5.0.3 on 2024-04-17 01:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_alter_album_numberofsongs_alter_artist_artistname'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='album',
            name='genre',
        ),
    ]