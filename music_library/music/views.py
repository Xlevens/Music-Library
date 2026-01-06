# music/views.py
# Complete Views for Cloud-Based Music Library
# Author: Laiba Imran

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.http import JsonResponse, HttpResponse, FileResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_POST
from .models import (
    Song, Playlist, Artist, Album, Genre, 
    Favorite, PlayHistory, Comment, Rating
)
from .forms import (
    SongUploadForm, PlaylistForm, SongSearchForm,
    CommentForm, RatingForm
)


# ============================================
# HOME AND DASHBOARD VIEWS
# ============================================

@login_required
def home(request):
    """
    Home page view
    Displays recent songs, popular songs, and user's playlists
    """
    # Get recent songs (last 10)
    recent_songs = Song.objects.filter(is_public=True).order_by('-upload_date')[:10]
    
    # Get popular songs (by play count)
    popular_songs = Song.objects.filter(is_public=True).order_by('-play_count')[:10]
    
    # Get featured songs
    featured_songs = Song.objects.filter(is_public=True, is_featured=True)[:5]
    
    # Get user's playlists
    user_playlists = request.user.playlists.all()[:5]
    
    # Get user's recent play history
    recent_plays = PlayHistory.objects.filter(user=request.user)[:5]
    
    # Get statistics
    total_songs = Song.objects.filter(is_public=True).count()
    total_artists = Artist.objects.count()
    total_albums = Album.objects.count()
    
    context = {
        'recent_songs': recent_songs,
        'popular_songs': popular_songs,
        'featured_songs': featured_songs,
        'user_playlists': user_playlists,
        'recent_plays': recent_plays,
        'total_songs': total_songs,
        'total_artists': total_artists,
        'total_albums': total_albums,
    }
    return render(request, 'music/home.html', context)


# ============================================
# SONG VIEWS
# ============================================

@login_required
def song_list(request):
    """
    List all songs with filtering options
    """
    # Get all songs (public + user's private songs)
    songs = Song.objects.filter(
        Q(is_public=True) | Q(uploaded_by=request.user)
    ).select_related('artist', 'album', 'genre')
    
    # Filter by genre
    genre_id = request.GET.get('genre')
    if genre_id:
        songs = songs.filter(genre_id=genre_id)
    
    # Filter by artist
    artist_id = request.GET.get('artist')
    if artist_id:
        songs = songs.filter(artist_id=artist_id)
    
    # Filter by album
    album_id = request.GET.get('album')
    if album_id:
        songs = songs.filter(album_id=album_id)
    
    # Sort options
    sort_by = request.GET.get('sort', '-upload_date')
    valid_sorts = ['-upload_date', 'title', '-play_count', 'artist__name']
    if sort_by in valid_sorts:
        songs = songs.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(songs, 20)  # 20 songs per page
    page = request.GET.get('page')
    
    try:
        songs = paginator.page(page)
    except PageNotAnInteger:
        songs = paginator.page(1)
    except EmptyPage:
        songs = paginator.page(paginator.num_pages)
    
    # Get filter options
    genres = Genre.objects.all()
    artists = Artist.objects.all()
    albums = Album.objects.all()
    
    context = {
        'songs': songs,
        'genres': genres,
        'artists': artists,
        'albums': albums,
        'current_genre': genre_id,
        'current_artist': artist_id,
        'current_album': album_id,
        'current_sort': sort_by,
    }
    return render(request, 'music/song_list.html', context)


@login_required
def song_detail(request, pk):
    """
    Song detail view
    Display full song information and player
    """
    song = get_object_or_404(Song, pk=pk)
    
    # Check if user can access this song
    if not song.is_public and song.uploaded_by != request.user:
        messages.error(request, 'You do not have permission to view this song.')
        return redirect('music:home')
    
    # Check if song is in user's favorites
    is_favorite = Favorite.objects.filter(user=request.user, song=song).exists()
    
    # Get user's rating for this song
    user_rating = Rating.objects.filter(user=request.user, song=song).first()
    
    # Get average rating
    avg_rating = song.ratings.aggregate(Avg('rating'))['rating__avg']
    rating_count = song.ratings.count()
    
    # Get comments
    comments = song.comments.select_related('user').order_by('-created_at')
    
    # Get related songs (same artist or genre)
    related_songs = Song.objects.filter(
        Q(artist=song.artist) | Q(genre=song.genre)
    ).exclude(pk=song.pk).filter(is_public=True)[:6]
    
    # Forms
    comment_form = CommentForm()
    rating_form = RatingForm(initial={'rating': user_rating.rating if user_rating else None})
    
    context = {
        'song': song,
        'is_favorite': is_favorite,
        'user_rating': user_rating,
        'avg_rating': avg_rating,
        'rating_count': rating_count,
        'comments': comments,
        'related_songs': related_songs,
        'comment_form': comment_form,
        'rating_form': rating_form,
    }
    return render(request, 'music/song_detail.html', context)


@login_required
def upload_song(request):
    """
    Upload new song
    """
    if request.method == 'POST':
        form = SongUploadForm(request.POST, request.FILES)
        if form.is_valid():
            song = form.save(commit=False)
            song.uploaded_by = request.user
            song.save()
            messages.success(request, f'Song "{song.title}" uploaded successfully!')
            return redirect('music:song_detail', pk=song.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SongUploadForm()
    
    context = {'form': form}
    return render(request, 'music/upload_song.html', context)


@login_required
def edit_song(request, pk):
    """
    Edit song details
    """
    song = get_object_or_404(Song, pk=pk)
    
    # Only uploader can edit
    if song.uploaded_by != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit this song.')
        return redirect('music:song_detail', pk=song.pk)
    
    if request.method == 'POST':
        form = SongUploadForm(request.POST, request.FILES, instance=song)
        if form.is_valid():
            form.save()
            messages.success(request, f'Song "{song.title}" updated successfully!')
            return redirect('music:song_detail', pk=song.pk)
    else:
        form = SongUploadForm(instance=song)
    
    context = {'form': form, 'song': song}
    return render(request, 'music/edit_song.html', context)


@login_required
@require_POST
def delete_song(request, pk):
    """
    Delete song
    """
    song = get_object_or_404(Song, pk=pk)
    
    # Only uploader or admin can delete
    if song.uploaded_by != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this song.')
        return redirect('music:song_detail', pk=song.pk)
    
    song_title = song.title
    song.delete()
    messages.success(request, f'Song "{song_title}" deleted successfully.')
    return redirect('music:song_list')


@login_required
def play_song(request, pk):
    """
    Record song play and increment play count
    """
    song = get_object_or_404(Song, pk=pk)
    
    # Increment play count
    song.increment_play_count()
    
    # Create play history record
    PlayHistory.objects.create(user=request.user, song=song)
    
    return JsonResponse({
        'status': 'success',
        'play_count': song.play_count,
        'message': f'Playing {song.title}'
    })


@login_required
def download_song(request, pk):
    """
    Download song file
    """
    song = get_object_or_404(Song, pk=pk)
    
    # Check permissions
    if not song.is_public and song.uploaded_by != request.user:
        messages.error(request, 'You do not have permission to download this song.')
        return redirect('music:home')
    
    # Increment download count
    song.increment_download_count()
    
    # Serve file
    response = FileResponse(song.audio_file.open('rb'))
    response['Content-Disposition'] = f'attachment; filename="{song.file_name}"'
    return response


# ============================================
# SEARCH VIEWS
# ============================================

@login_required
def search(request):
    """
    Search songs, artists, albums
    """
    query = request.GET.get('q', '').strip()
    
    songs = Song.objects.none()
    artists = Artist.objects.none()
    albums = Album.objects.none()
    
    if query:
        # Search songs
        songs = Song.objects.filter(
            Q(title__icontains=query) | 
            Q(artist__name__icontains=query) |
            Q(album__title__icontains=query) |
            Q(lyrics__icontains=query)
        ).filter(
            Q(is_public=True) | Q(uploaded_by=request.user)
        ).distinct()[:50]
        
        # Search artists
        artists = Artist.objects.filter(name__icontains=query)[:20]
        
        # Search albums
        albums = Album.objects.filter(
            Q(title__icontains=query) | 
            Q(artist__name__icontains=query)
        )[:20]
    
    context = {
        'query': query,
        'songs': songs,
        'artists': artists,
        'albums': albums,
        'song_count': songs.count(),
        'artist_count': artists.count(),
        'album_count': albums.count(),
    }
    return render(request, 'music/search.html', context)


# ============================================
# PLAYLIST VIEWS
# ============================================

@login_required
def playlist_list(request):
    """
    List user's playlists
    """
    # User's own playlists
    my_playlists = request.user.playlists.all()
    
    # Public playlists from other users
    public_playlists = Playlist.objects.filter(
        is_public=True
    ).exclude(user=request.user)[:10]
    
    context = {
        'my_playlists': my_playlists,
        'public_playlists': public_playlists,
    }
    return render(request, 'music/playlist_list.html', context)


@login_required
def playlist_detail(request, pk):
    """
    Playlist detail view
    """
    playlist = get_object_or_404(Playlist, pk=pk)
    
    # Check permission
    if not playlist.is_public and playlist.user != request.user:
        messages.error(request, 'You do not have permission to view this playlist.')
        return redirect('music:playlist_list')
    
    songs = playlist.songs.all()
    
    context = {
        'playlist': playlist,
        'songs': songs,
        'is_owner': playlist.user == request.user,
    }
    return render(request, 'music/playlist_detail.html', context)


@login_required
def create_playlist(request):
    """
    Create new playlist
    """
    if request.method == 'POST':
        form = PlaylistForm(request.POST, request.FILES)
        if form.is_valid():
            playlist = form.save(commit=False)
            playlist.user = request.user
            playlist.save()
            messages.success(request, f'Playlist "{playlist.name}" created successfully!')
            return redirect('music:playlist_detail', pk=playlist.pk)
    else:
        form = PlaylistForm()
    
    context = {'form': form}
    return render(request, 'music/create_playlist.html', context)


@login_required
def edit_playlist(request, pk):
    """
    Edit playlist
    """
    playlist = get_object_or_404(Playlist, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = PlaylistForm(request.POST, request.FILES, instance=playlist)
        if form.is_valid():
            form.save()
            messages.success(request, f'Playlist "{playlist.name}" updated successfully!')
            return redirect('music:playlist_detail', pk=playlist.pk)
    else:
        form = PlaylistForm(instance=playlist)
    
    context = {'form': form, 'playlist': playlist}
    return render(request, 'music/edit_playlist.html', context)


@login_required
@require_POST
def delete_playlist(request, pk):
    """
    Delete playlist
    """
    playlist = get_object_or_404(Playlist, pk=pk, user=request.user)
    playlist_name = playlist.name
    playlist.delete()
    messages.success(request, f'Playlist "{playlist_name}" deleted successfully.')
    return redirect('music:playlist_list')


@login_required
def add_to_playlist(request, song_pk):
    """
    Add song to playlist
    """
    song = get_object_or_404(Song, pk=song_pk)
    playlists = request.user.playlists.all()
    
    if request.method == 'POST':
        playlist_id = request.POST.get('playlist_id')
        playlist = get_object_or_404(Playlist, pk=playlist_id, user=request.user)
        
        # Check if song already in playlist
        if playlist.songs.filter(pk=song.pk).exists():
            messages.warning(request, f'"{song.title}" is already in "{playlist.name}"')
        else:
            playlist.songs.add(song)
            messages.success(request, f'Added "{song.title}" to "{playlist.name}"')
        
        return redirect('music:song_detail', pk=song.pk)
    
    context = {
        'song': song,
        'playlists': playlists,
    }
    return render(request, 'music/add_to_playlist.html', context)


@login_required
@require_POST
def remove_from_playlist(request, playlist_pk, song_pk):
    """
    Remove song from playlist
    """
    playlist = get_object_or_404(Playlist, pk=playlist_pk, user=request.user)
    song = get_object_or_404(Song, pk=song_pk)
    
    playlist.songs.remove(song)
    messages.success(request, f'Removed "{song.title}" from "{playlist.name}"')
    
    return redirect('music:playlist_detail', pk=playlist.pk)


# ============================================
# FAVORITE VIEWS
# ============================================

@login_required
@require_POST
def toggle_favorite(request, song_pk):
    """
    Toggle favorite status for a song
    """
    song = get_object_or_404(Song, pk=song_pk)
    favorite, created = Favorite.objects.get_or_create(user=request.user, song=song)
    
    if not created:
        favorite.delete()
        is_favorite = False
        messages.info(request, f'Removed "{song.title}" from favorites')
    else:
        is_favorite = True
        messages.success(request, f'Added "{song.title}" to favorites')
    
    # Return JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'is_favorite': is_favorite})
    
    return redirect('music:song_detail', pk=song.pk)


@login_required
def favorites(request):
    """
    List user's favorite songs
    """
    favorites = Favorite.objects.filter(user=request.user).select_related('song')
    
    context = {'favorites': favorites}
    return render(request, 'music/favorites.html', context)


# ============================================
# ARTIST & ALBUM VIEWS
# ============================================

@login_required
def artist_list(request):
    """
    List all artists
    """
    artists = Artist.objects.annotate(
        song_count=Count('songs')
    ).order_by('name')
    
    # Pagination
    paginator = Paginator(artists, 24)
    page = request.GET.get('page')
    
    try:
        artists = paginator.page(page)
    except PageNotAnInteger:
        artists = paginator.page(1)
    except EmptyPage:
        artists = paginator.page(paginator.num_pages)
    
    context = {'artists': artists}
    return render(request, 'music/artist_list.html', context)


@login_required
def artist_detail(request, pk):
    """
    Artist detail view
    """
    artist = get_object_or_404(Artist, pk=pk)
    songs = artist.songs.filter(Q(is_public=True) | Q(uploaded_by=request.user))
    albums = artist.albums.all()
    
    context = {
        'artist': artist,
        'songs': songs,
        'albums': albums,
    }
    return render(request, 'music/artist_detail.html', context)


@login_required
def album_detail(request, pk):
    """
    Album detail view
    """
    album = get_object_or_404(Album, pk=pk)
    songs = album.songs.filter(Q(is_public=True) | Q(uploaded_by=request.user))
    
    context = {
        'album': album,
        'songs': songs,
    }
    return render(request, 'music/album_detail.html', context)


# ============================================
# COMMENT & RATING VIEWS
# ============================================

@login_required
@require_POST
def add_comment(request, song_pk):
    """
    Add comment to song
    """
    song = get_object_or_404(Song, pk=song_pk)
    form = CommentForm(request.POST)
    
    if form.is_valid():
        comment = form.save(commit=False)
        comment.song = song
        comment.user = request.user
        comment.save()
        messages.success(request, 'Comment added successfully!')
    else:
        messages.error(request, 'Error adding comment.')
    
    return redirect('music:song_detail', pk=song.pk)


@login_required
@require_POST
def add_rating(request, song_pk):
    """
    Add or update rating for song
    """
    song = get_object_or_404(Song, pk=song_pk)
    form = RatingForm(request.POST)
    
    if form.is_valid():
        rating_value = form.cleaned_data['rating']
        rating, created = Rating.objects.update_or_create(
            user=request.user,
            song=song,
            defaults={'rating': rating_value}
        )
        
        if created:
            messages.success(request, f'Rated "{song.title}" {rating_value}/5 stars!')
        else:
            messages.success(request, f'Updated rating to {rating_value}/5 stars!')
    
    return redirect('music:song_detail', pk=song.pk)


# ============================================
# HISTORY & STATS VIEWS
# ============================================

@login_required
def play_history(request):
    """
    View user's play history
    """
    history = PlayHistory.objects.filter(
        user=request.user
    ).select_related('song').order_by('-played_at')
    
    # Pagination
    paginator = Paginator(history, 50)
    page = request.GET.get('page')
    
    try:
        history = paginator.page(page)
    except PageNotAnInteger:
        history = paginator.page(1)
    except EmptyPage:
        history = paginator.page(paginator.num_pages)
    
    context = {'history': history}
    return render(request, 'music/play_history.html', context)


@login_required
def user_stats(request):
    """
    Display user statistics
    """
    total_uploads = request.user.uploaded_songs.count()
    total_playlists = request.user.playlists.count()
    total_favorites = request.user.favorites.count()
    total_plays = PlayHistory.objects.filter(user=request.user).count()
    
    # Most played songs
    most_played = PlayHistory.objects.filter(
        user=request.user
    ).values('song').annotate(
        play_count=Count('song')
    ).order_by('-play_count')[:10]
    
    most_played_songs = []
    for item in most_played:
        song = Song.objects.get(pk=item['song'])
        most_played_songs.append({
            'song': song,
            'plays': item['play_count']
        })
    
    context = {
        'total_uploads': total_uploads,
        'total_playlists': total_playlists,
        'total_favorites': total_favorites,
        'total_plays': total_plays,
        'most_played_songs': most_played_songs,
    }
    return render(request, 'music/user_stats.html', context)