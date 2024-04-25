from django.contrib import admin

from.models import Listener, Artist, Song, Album, Genre, LikeInteraction

# Register your models here.
admin.site.register(Listener)
admin.site.register(Artist)
admin.site.register(Song)
admin.site.register(Album)
admin.site.register(Genre)
admin.site.register(LikeInteraction)
