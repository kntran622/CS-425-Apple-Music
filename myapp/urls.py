from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path('artistHome/', views.artistHome, name='artistHome'),
    path('songHome/', views.songHome, name='songHome'),
    path('albumHome/', views.albumHome, name='albumHome'),
    path('listenerHome/', views.listenerHome, name='listenerHome'),
    path('listenerLikedSongs/<int:listenerID>/', views.listenerLikedSongs, name='listenerLikedSongs'),
    path('recommendedSong/<int:songID>/', views.recommendedSong, name='recommendedSong'),
    path('artistPage/<artistID>', views.artistPage, name='artistPage'),
    path('albumPage/<albumID>', views.albumPage, name='albumPage'),
    path('genreHome/<str:genre>/', views.genreHome, name='genreHome'),
    path("addArtist/", views.add_artist_view, name="addArtist"),
    path("updateArtist/<artistID>", views.update_artist_view, name="updateArtist"),
    path("deleteArtist/<artistID>", views.delete_artist_view, name="deleteArtist"),
    path("addAlbum/", views.add_album_view, name="addAlbum"),
    path("updateAlbum/<albumID>", views.update_album_view, name="updateAlbum"),
    path("deleteAlbum/<albumID>", views.delete_album_view, name="deleteAlbum"),
    path("addSong/", views.add_song_view, name="addSong"),
    path("updateSong/<songID>", views.update_song_view, name="updateSong"),
    path("deleteSong/<songID>", views.delete_song_view, name="deleteSong")
]