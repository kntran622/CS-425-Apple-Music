from django.shortcuts import render, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.http import HttpResponseRedirect
from .models import *;
from .forms import *;
from django.db.models import Q, Sum
from django.db import connection

def update_number_of_songs(album):
    """
    Update the numberOfSongs attribute of the given album to the correct amount.
    """
    num_songs = Song.objects.filter(albumID=album.albumID).count()
    album.numberOfSongs = num_songs
    album.save()

def convert_length(length_in_seconds):
    minutes = length_in_seconds // 60
    seconds = length_in_seconds % 60
    return f"{minutes:02d}:{seconds:02d}"

# Create your views here.
def home(request):
    albums = Album.objects.all()
    for album in albums:
        update_number_of_songs(album)
    return render(request, "myapp/home.html", {
        "songs": Song.objects.all(),
        "artists": Artist.objects.all(),
        "albums": albums,
        "genres": Genre.objects.all()
    })

def artistHome(request):
    # Define base SQL query for artists
    sql_query = """
        SELECT *, (
            SELECT SUM(myapp_song.streams)
            FROM myapp_song
            WHERE myapp_song.artistID_id = myapp_artist.artistID
        ) AS totalStreams,
        (
            SELECT AVG(myapp_song.streams)
            FROM myapp_song
            WHERE myapp_song.artistID_id = myapp_artist.artistID
        ) AS averageStreams
        FROM myapp_artist
    """

    # Execute SQL query to fetch artists
    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        artists_data = cursor.fetchall()

    # Define a dictionary to store artist objects
    artists_dict = {}

    # Populate artists_dict with artist objects
    for artist_data in artists_data:
        artist = {
            'artistID': artist_data[0],
            'artistName': artist_data[1],
            'bio': artist_data[2],
            'birthDate': artist_data[3] or 0,
            'hometown': artist_data[4] or 0,
            'totalStreams': artist_data[8],
            'averageStreams': artist_data[9],
        }
        artists_dict[artist['artistID']] = artist

    print(artists_data)

    # Define the mapping of sort options to SQL order by clauses
    sort_options_sql = {
        'highest_total_streams': 'ORDER BY totalStreams DESC',
        'lowest_total_streams': 'ORDER BY totalStreams ASC',
        'oldest': 'ORDER BY birthDate ASC',
        'youngest': 'ORDER BY birthDate DESC',
        'newest': 'ORDER BY birthDate DESC',
        'highest_average_streams': 'ORDER BY averageStreams DESC',
        'lowest_average_streams': 'ORDER BY averageStreams ASC',
    }

    # Get the sort option from the request, defaulting to 'newest'
    sort_option = request.GET.get('sort', 'newest')

    # Default sort option is the highest artistID (most recently added)
    if sort_option == 'newest':
        sort_options_sql['newest'] = 'ORDER BY artistID DESC'

    # Add order by clause to the SQL query
    sql_query += ' ' + sort_options_sql.get(sort_option, 'ORDER BY artistID DESC')

    # Execute the modified SQL query
    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        artists_data = cursor.fetchall()

    # Populate artists_dict with sorted artist objects
    sorted_artists = []
    for artist_data in artists_data:
        artist = {
            'artistID': artist_data[0],
            'artistName': artist_data[1],
            'birthDate': artist_data[2],
            'totalStreams': artist_data[3] or 0,
            'averageStreams': artist_data[4] or 0,
        }
        sorted_artists.append(artist)

    context = {
        'artists': sorted_artists,
        'sort_option': sort_option,
    }
    return render(request, 'myapp/artistHome.html', context)

def update_number_of_songs(album):
    """
    Update the numberOfSongs attribute of the given album to the correct amount.
    """
    num_songs = Song.objects.filter(albumID=album.albumID).count()
    album.numberOfSongs = num_songs
    album.save()

def albumHome(request):
    # Fetch all albums
    albums = Album.objects.all()
    
    # Update each album's totalStreams and numberOfSongs
    for album in albums:
        total_streams = Song.objects.filter(albumID=album.albumID).aggregate(total_streams=Sum('streams'))['total_streams'] or 0
        album.totalStreams = total_streams
        update_number_of_songs(album)
        if album.numberOfSongs > 0:
            album.averageStreams = round(total_streams / album.numberOfSongs)
        else:
            album.averageStreams = 0
        album.save()

    # Get the sort option from the request, defaulting to 'newest'
    sort_option = request.GET.get('sort', 'newest')

    # Define SQL queries for sorting options
    if sort_option == 'highest_total_streams':
        sql_query = """
            SELECT *, COALESCE(total_streams, 0) AS total_streams, artistName
            FROM myapp_album
            LEFT JOIN (
                SELECT albumID_id, SUM(streams) AS total_streams
                FROM myapp_song
                GROUP BY albumID_id
            ) AS song_streams ON myapp_album.albumID = song_streams.albumID_id
            LEFT JOIN myapp_artist ON myapp_album.artistID_id = myapp_artist.artistID
            ORDER BY total_streams DESC
        """
    elif sort_option == 'lowest_total_streams':
        sql_query = """
            SELECT *, COALESCE(total_streams, 0) AS total_streams, artistName
            FROM myapp_album
            LEFT JOIN (
                SELECT albumID_id, SUM(streams) AS total_streams
                FROM myapp_song
                GROUP BY albumID_id
            ) AS song_streams ON myapp_album.albumID = song_streams.albumID_id
            LEFT JOIN myapp_artist ON myapp_album.artistID_id = myapp_artist.artistID
            ORDER BY total_streams ASC
        """
    elif sort_option == 'oldest':
        sql_query = """
            SELECT *, artistName
            FROM myapp_album
            LEFT JOIN myapp_artist ON myapp_album.artistID_id = myapp_artist.artistID
            ORDER BY releaseDate ASC
        """
    elif sort_option == 'newest':
        sql_query = """
            SELECT *, artistName
            FROM myapp_album
            LEFT JOIN myapp_artist ON myapp_album.artistID_id = myapp_artist.artistID
            ORDER BY releaseDate DESC
        """
    elif sort_option == 'highest_average_streams_per_song':
        sql_query = """
            SELECT *, COALESCE(total_streams / numberOfSongs, 0) AS avg_streams_per_song, artistName
            FROM (
                SELECT *, COALESCE(total_streams, 0) AS total_streams, COALESCE(number_of_songs, 0) AS numberOfSongs
                FROM myapp_album
                LEFT JOIN (
                    SELECT albumID_id, SUM(streams) AS total_streams, COUNT(songID) AS number_of_songs
                    FROM myapp_song
                    GROUP BY albumID_id
                ) AS song_info ON myapp_album.albumID = song_info.albumID_id
            ) AS album_stats
            LEFT JOIN myapp_artist ON album_stats.artistID_id = myapp_artist.artistID
            ORDER BY avg_streams_per_song DESC
        """
    elif sort_option == 'lowest_average_streams_per_song':
        sql_query = """
            SELECT *, COALESCE(total_streams / numberOfSongs, 0) AS avg_streams_per_song, artistName
            FROM (
                SELECT *, COALESCE(total_streams, 0) AS total_streams, COALESCE(number_of_songs, 0) AS numberOfSongs
                FROM myapp_album
                LEFT JOIN (
                    SELECT albumID_id, SUM(streams) AS total_streams, COUNT(songID) AS number_of_songs
                    FROM myapp_song
                    GROUP BY albumID_id
                ) AS song_info ON myapp_album.albumID = song_info.albumID_id
            ) AS album_stats
            LEFT JOIN myapp_artist ON album_stats.artistID_id = myapp_artist.artistID
            ORDER BY avg_streams_per_song ASC
        """

    # Execute the SQL query
    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        # Fetch all albums from the cursor
        albums_data = cursor.fetchall()

    # Extract the album attributes
    albums = []
    for album_data in albums_data:
        album_dict = {
            'albumID': album_data[0],
            'albumName': album_data[1],
            'numberOfSongs': album_data[2],
            'length': album_data[3],
            'releaseDate': album_data[5],
            'description': album_data[5],
            'totalStreams': album_data[8],
            'averageStreams': album_data[7],
            'genre_id': album_data[8],
            'artistName': album_data[11],  # Add artistName attribute
        }
        albums.append(album_dict)

    for data in album_data:
        print(data)

    context = {
        'albums': albums,
        'sort_option': sort_option,
    }
    return render(request, 'myapp/albumHome.html', context)

def songHome(request):
    # Fetch all genres
    genres = Genre.objects.all()

    # Get the search query from the request
    search_query = request.GET.get('search', '')

    # Get the selected genres from the URL query string
    selected_genres = request.GET.getlist('genre')

    # Define the base SQL query for songs with artist and album details
    sql_query = """
        SELECT myapp_song.songID, myapp_song.songName, myapp_song.releaseDate,
               myapp_song.streams, myapp_artist.artistName, myapp_album.albumName, myapp_genre.name,
               myapp_song.length
        FROM myapp_song
        INNER JOIN myapp_artist ON myapp_song.artistID_id = myapp_artist.artistID
        INNER JOIN myapp_album ON myapp_song.albumID_id = myapp_album.albumID
        INNER JOIN myapp_genre ON myapp_song.genre_id = myapp_genre.genreID
    """

    # Define parameters for the SQL query
    params = []

    # Apply genre filter
    if selected_genres:
        sql_query += " WHERE myapp_genre.name IN (" + ",".join(["%s" for _ in selected_genres]) + ")"
        params.extend(selected_genres)

    # Apply search filter
    if search_query:
        sql_query += " AND (myapp_song.songName ILIKE %s OR myapp_artist.artistName ILIKE %s OR myapp_album.albumName ILIKE %s)"
        params.extend(['%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%'])

    # Define the mapping of sort options to SQL order by clauses
    sort_options = {
        'newest': 'ORDER BY myapp_song.releaseDate DESC',
        'highest_streams': 'ORDER BY myapp_song.streams DESC',
        'lowest_streams': 'ORDER BY myapp_song.streams ASC',
        'oldest': 'ORDER BY myapp_song.releaseDate ASC',
    }

    # Get the sort option from the request, defaulting to 'newest'
    sort_option = request.GET.get('sort', 'newest')

    # Add order by clause to the SQL query
    sql_query += ' ' + sort_options.get(sort_option, 'ORDER BY myapp_song.releaseDate DESC')

    # Execute the SQL query with parameters
    with connection.cursor() as cursor:
        cursor.execute(sql_query, params)
        songs_data = cursor.fetchall()

    # Construct list of song dictionaries from fetched data
    songs = []
    for song_data in songs_data:
        song_dict = {
            'songID': song_data[0],
            'songName': song_data[1],
            'releaseDate': song_data[2],
            'streams': song_data[3],
            'artistName': song_data[4],
            'albumName': song_data[5],
            'genre': song_data[6],
            'length': song_data[7],  # Length in seconds
        }
        songs.append(song_dict)

    for data in songs_data:
        print(data)

    context = {
        'songs': songs,
        'genres': genres,
        'sort_option': sort_option,
        'search_query': search_query,
        'selected_genres': selected_genres,  # Pass selected genres to template
    }
    return render(request, 'myapp/songHome.html', context)

def listenerHome(request):
    # Get all listeners
    listeners = Listener.objects.all()
    context = {'listeners': listeners}
    return render(request, 'myapp/listenerHome.html', context)

def listenerLikedSongs(request, listenerID):
    # Get the listener by ID
    listener = Listener.objects.get(listenerID=listenerID)
    # Get all the liked songs of the listener
    liked_songs = listener.likeinteraction_set.all()
    context = {
        'listener': listener,
        'liked_songs': liked_songs
    }
    return render(request, 'myapp/listenerLikedSongs.html', context)

from django.db import connection
from myapp.models import Song, LikeInteraction
from django.shortcuts import render

def recommendedSong(request, songID):
    # Define the SQL query to get the listenerIDs who liked the given song
    listener_query = """
        SELECT DISTINCT listener_id
        FROM myapp_likeinteraction
        WHERE song_id = %s
    """

    # Execute the SQL query to get the listenerIDs
    with connection.cursor() as cursor:
        cursor.execute(listener_query, [songID])
        listeners = [row[0] for row in cursor.fetchall()]

    # Initialize a dictionary to store the count of liked songs for each song
    song_counts = {}

    # Iterate over each listener
    for listener in listeners:
        # Define the SQL query to get the songIDs liked by the current listener
        liked_songs_query = """
            SELECT song_id
            FROM myapp_likeinteraction
            WHERE listener_id = %s AND song_id != %s
        """

        # Execute the SQL query to get the liked songIDs
        with connection.cursor() as cursor:
            cursor.execute(liked_songs_query, [listener, songID])
            liked_songs = [row[0] for row in cursor.fetchall()]
        
        # Count the occurrences of each song
        for liked_song in liked_songs:
            if liked_song in song_counts:
                song_counts[liked_song] += 1
            else:
                song_counts[liked_song] = 1

    # Sort the dictionary by value (number of occurrences) in descending order
    sorted_song_counts = sorted(song_counts.items(), key=lambda x: x[1], reverse=True)

    # Get the songID of the recommended song (the second most commonly liked song)
    if len(sorted_song_counts) > 1:
        recommended_songID = sorted_song_counts[1][0]  # Second most commonly liked song
    else:
        # If there's only one song (the given song), return None
        recommended_songID = None

    # Get the original song object
    try:
        original_song = Song.objects.get(songID=songID)
    except Song.DoesNotExist:
        # Handle the case where the original song doesn't exist
        original_song = None

    # Get the recommended song object
    recommended_song = None
    if recommended_songID:
        # Retrieve the recommended song object using Django ORM
        recommended_song = Song.objects.get(songID=recommended_songID)

    # Find the list of common listeners who liked both the original and recommended songs
    common_listeners = []
    common_listeners_count = 0
    
    if original_song and recommended_song:
        # Define the SQL query to find common listeners
        common_listeners_query = """
            SELECT DISTINCT listener.listenerName
            FROM myapp_likeinteraction
            INNER JOIN myapp_listener listener ON listener.listenerID = myapp_likeinteraction.listener_id
            WHERE song_id = %s
            AND listener_id IN (
                SELECT DISTINCT listener_id
                FROM myapp_likeinteraction
                WHERE song_id = %s
            )
        """
        # Execute the SQL query to get common listeners
        with connection.cursor() as cursor:
            cursor.execute(common_listeners_query, [songID, recommended_songID])
            common_listeners = cursor.fetchall()
            common_listeners_count = len(common_listeners)
    
    context = {
        'original_song': original_song,
        'recommended_song': recommended_song,
        'common_listeners': common_listeners,
        'common_listeners_count': common_listeners_count,
    }
    return render(request, 'myapp/recommendedSong.html', context)






def artistPage(request, artistID):
    # Retrieve entities based on the genre
    artist = Artist.objects.get(pk=artistID)
    total_streams = Song.objects.filter(artistID=artist.artistID).aggregate(total_streams=Sum('streams'))['total_streams'] or 0
    artist.totalStreams = total_streams
    total_songs = Song.objects.filter(artistID=artist.artistID).count()
    if total_songs > 0:
        artist.averageStreams = round(total_streams / total_songs)
    else:
        artist.averageStreams = 0
    return render(request, 'myapp/artistPage.html', {
        "artist": artist,
        "albums": Album.objects.filter(artistID=artistID),
        "songs": Song.objects.filter(artistID=artistID)
    })

def albumPage(request, albumID):
    # Retrieve album details
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT myapp_album.albumID, myapp_album.albumName, myapp_album.releaseDate, myapp_artist.artistName, myapp_genre.name,
                   ROUND(AVG(myapp_song.streams)) as avg_streams
            FROM myapp_album
            INNER JOIN myapp_artist ON myapp_album.artistID_id = myapp_artist.artistID
            INNER JOIN myapp_genre ON myapp_album.genre_id = myapp_genre.genreID
            INNER JOIN myapp_song ON myapp_album.albumID = myapp_song.albumID_id
            WHERE myapp_album.albumID = %s
            GROUP BY myapp_album.albumID, myapp_album.albumName, myapp_album.releaseDate, myapp_artist.artistName, myapp_genre.name
            """,
            [albumID]
        )
        album_data = cursor.fetchone()

    if album_data:
        album = {
            'albumID': album_data[0],
            'albumName': album_data[1],
            'releaseDate': album_data[2],
            'artistName': album_data[3],
            'genre': album_data[4],
            'averageStreams': album_data[5],  # Average streams
        }

        # Retrieve songs for the album
        sql_query = """
            SELECT myapp_song.songID, myapp_song.songName, myapp_song.releaseDate, 
                   myapp_song.streams, myapp_artist.artistName, myapp_genre.name
            FROM myapp_song
            INNER JOIN myapp_artist ON myapp_song.artistID_id = myapp_artist.artistID
            INNER JOIN myapp_genre ON myapp_song.genre_id = myapp_genre.genreID
            WHERE myapp_song.albumID_id = %s
        """
        params = [albumID]

        # Get the search query from the request
        search_query = request.GET.get('search', '')

        # Apply search filter
        if search_query:
            sql_query += " AND (myapp_song.songName ILIKE %s)"
            params.append('%' + search_query + '%')

        # Define the mapping of sort options to SQL order by clauses
        sort_options = {
            'newest': 'ORDER BY myapp_song.releaseDate DESC',
            'highest_streams': 'ORDER BY myapp_song.streams DESC',
            'lowest_streams': 'ORDER BY myapp_song.streams ASC',
            'oldest': 'ORDER BY myapp_song.releaseDate ASC',
        }

        # Get the sort option from the request, defaulting to 'newest'
        sort_option = request.GET.get('sort', 'newest')

        # Add order by clause to the SQL query
        sql_query += ' ' + sort_options.get(sort_option, 'ORDER BY myapp_song.releaseDate DESC')

        # Execute the SQL query with parameters
        with connection.cursor() as cursor:
            cursor.execute(sql_query, params)
            songs_data = cursor.fetchall()

        # Construct list of song dictionaries from fetched data
        songs = []
        for song_data in songs_data:
            song_dict = {
                'songID': song_data[0],
                'songName': song_data[1],
                'releaseDate': song_data[2],
                'streams': song_data[3],
                'artistName': song_data[4],
                'genre': song_data[5],
            }
            songs.append(song_dict)

        context = {
            'album': album,
            'songs': songs,
            'sort_option': sort_option,
            'search_query': search_query,
        }
        return render(request, 'myapp/albumPage.html', context)
    else:
        return render(request, 'myapp/albumPage.html', {'error': 'Album not found'})

def genreHome(request, genre):
    # Retrieve entities based on the genre
    return render(request, 'myapp/genreHome.html', {
        "artists": Artist.objects.filter(genre=genre),
        "albums": Album.objects.filter(genre=genre),
        "songs": Song.objects.filter(genre=genre)
    })

def add_artist_view(request):
    if request.method == "POST":
        form = ArtistForm(request.POST)  # Instantiate the form with POST data
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ArtistForm()  # Instantiate the form without any data
    return render(request, 'myapp/addArtist.html', {'form': form})

def update_artist_view(request, artistID):
    artist = Artist.objects.get(pk=artistID)
    form = ArtistForm(request.POST or None, instance=artist)
    if form.is_valid():
            form.save()
            return redirect('home')
    return render(request, 'myapp/updateArtist.html', {
        "artist": artist,
        "form": form
    })

def delete_artist_view(request, artistID):
    artist = Artist.objects.get(pk=artistID)
    artist.delete()
    return redirect('home')

def add_album_view(request):
    if request.method == "POST":
        form = AlbumForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = AlbumForm()
    return render(request, 'myapp/addAlbum.html', {'form': form})

def update_album_view(request, albumID):
    album = Album.objects.get(pk=albumID)
    form = AlbumForm(request.POST or None, instance=album)
    if form.is_valid():
            form.save()
            return redirect('home')
    return render(request, 'myapp/updateAlbum.html', {
        "album": album,
        "form": form
    })

def delete_album_view(request, albumID):
    album = Album.objects.get(pk=albumID)
    album.delete()
    return redirect('home')

def add_song_view(request):
    form = SongForm(request.POST)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = SongForm()
    return render(request, 'myapp/addSong.html', {'form': form})

def update_song_view(request, songID):
    song = Song.objects.get(pk=songID)
    form = SongForm(request.POST or None, instance=song)
    if form.is_valid():
            form.save()
            return redirect('home')
    return render(request, 'myapp/updateSong.html', {
        "song": song,
        "form": form
    })

def delete_song_view(request, songID):
    song = Song.objects.get(pk=songID)
    song.delete()
    return redirect('home')