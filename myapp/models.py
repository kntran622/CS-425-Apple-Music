from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

# Create your models here.

class UserProfile(AbstractUser, models.Model):
    password = models.CharField(max_length=20)
    username = models.CharField(max_length=30, unique=True)

class Listener(models.Model):
    listenerID = models.AutoField(primary_key=True)
    listenerName = models.CharField(max_length=200, default='')

    def __str__(self):
        return self.listenerName

class LikeInteraction(models.Model):
    listener = models.ForeignKey(Listener, on_delete=models.CASCADE)
    song = models.ForeignKey('Song', on_delete=models.CASCADE)
    date = models.DateField()

    class Meta:
        # Define composite primary key
        constraints = [
            models.UniqueConstraint(fields=['listener', 'song', 'date'], name='unique_like')
        ]

    def __str__(self):
        return f"{self.listener.listenerName} likes {self.song.songName} on {self.date}"


class Artist(models.Model):
    artistID = models.AutoField(primary_key=True)
    artistName = models.CharField('Artist Name', max_length=100)
    bio = models.TextField()
    hometown = models.CharField(max_length=100)
    birthDate = models.DateField()
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE)
    totalStreams = models.IntegerField(default=0)
    averageStreams = models.IntegerField(default=0)
    def __str__(self) -> str:
        return self.artistName

class Song(models.Model):
    songID = models.AutoField(primary_key=True)
    songName = models.CharField(max_length=200)
    length = models.DurationField()
    genre = models.ForeignKey('Genre',max_length=100, on_delete=models.CASCADE)
    releaseDate = models.DateField()
    streams = models.IntegerField()
    artistID = models.ForeignKey('Artist', on_delete=models.CASCADE)
    albumID = models.ForeignKey('Album', on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.songName


class Album(models.Model):
    albumID = models.AutoField(primary_key=True)
    albumName = models.CharField(max_length=200)
    numberOfSongs = models.IntegerField(default=0)
    length = models.DurationField(default=0)
    releaseDate = models.DateField()
    description = models.TextField()
    totalStreams = models.IntegerField(default=0)
    averageStreams = models.IntegerField(default=0)
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE)
    artistID = models.ForeignKey(Artist, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.albumName
        
class Genre(models.Model):
    genreID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    totalStreams = models.IntegerField(default=0)
    averageStreams = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    

