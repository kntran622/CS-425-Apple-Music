# Generated by Django 5.0.3 on 2024-04-01 03:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_listener_delete_user_rename_albumid_album_albumid_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='artist',
            name='thumbnail',
        ),
    ]