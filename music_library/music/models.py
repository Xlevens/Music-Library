# music/models.py
# Complete Models for Cloud-Based Music Library
# Author: Laiba Imran

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from datetime import timedelta
import os

User = get_user_model()


class Genre(models.Model):
    """
    Music Genre Model
    Stores different music genres like Pop, Rock, Jazz, etc.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Genre'
        verbose_name_plural = 'Genres'
    
    def __str__(self):
        return self.name
    
    @property
    def song_count(self):
        """Returns the number of songs in this genre"""
        return self.songs.count()


class Artist(models.Model):
    """
    Artist Model
    Stores artist/band information
    """
    name = models.CharField(max_length=200)
    bio = models.TextField(blank=True, help_text="Artist biography")
    image = models.ImageField(
        upload_to='artists/', 
        blank=True, 
        null=True,
        help_text="Artist profile picture"
    )
    country = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Artist'
        verbose_name_plural = 'Artists'
        indexes = [
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def song_count(self):
        """Returns the number of songs by this artist"""
        return self.songs.count()
    
    @property
    def album_count(self):
        """Returns the number of albums by this artist"""
        return self.albums.count()


class Album(models.Model):
    """
    Album Model
    Stores album/collection information
    """
    title = models.CharField(max_length=200)
    artist = models.ForeignKey(
        Artist, 
        on_delete=models.CASCADE, 
        related_name='albums'
    )
    cover_image = models.ImageField(
        upload_to='album_covers/', 
        blank=True, 
        null=True,
        help_text="Album cover art"
    )
    release_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    record_label = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-release_date', 'title']
        verbose_name = 'Album'
        verbose_name_plural = 'Albums'
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['artist', 'release_date']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.artist.name}"
    
    @property
    def song_count(self):
        """Returns the number of songs in this album"""
        return self.songs.count()
    
    @property
    def total_duration(self):
        """Calculate total duration of all songs in album"""
        total = timedelta()
        for song in self.songs.all():
            if song.duration:
                total += song.duration
        return total


class Song(models.Model):
    """
    Song Model - Core music file
    Stores individual song information and audio files
    """
    title = models.CharField(max_length=200)
    artist = models.ForeignKey(
        Artist, 
        on_delete=models.CASCADE, 
        related_name='songs'
    )
    album = models.ForeignKey(
        Album, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='songs'
    )
    genre = models.ForeignKey(
        Genre, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='songs'
    )
    audio_file = models.FileField(
        upload_to='music_files/',
        validators=[
            FileExtensionValidator(
                allowed_extensions=['mp3', 'wav', 'ogg', 'm4a', 'flac']
            )
        ],
        help_text="Supported formats: MP3, WAV, OGG, M4A, FLAC"
    )
    duration = models.DurationField(
        null=True, 
        blank=True,
        help_text="Song duration (HH:MM:SS)"
    )
    lyrics = models.TextField(blank=True, help_text="Song lyrics")
    release_year = models.IntegerField(null=True, blank=True)
    
    # Upload information
    uploaded_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='uploaded_songs'
    )
    upload_date = models.DateTimeField(auto_now_add=True)
    
    # Statistics
    play_count = models.IntegerField(default=0)
    download_count = models.IntegerField(default=0)
    
    # Visibility
    is_public = models.BooleanField(
        default=True,
        help_text="Make this song visible to all users"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Feature this song on homepage"
    )
    
    class Meta:
        ordering = ['-upload_date']
        verbose_name = 'Song'
        verbose_name_plural = 'Songs'
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['artist']),
            models.Index(fields=['genre']),
            models.Index(fields=['-play_count']),
            models.Index(fields=['-upload_date']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.artist.name}"
    
    def increment_play_count(self):
        """Increment play count by 1"""
        self.play_count += 1
        self.save(update_fields=['play_count'])
    
    def increment_download_count(self):
        """Increment download count by 1"""
        self.download_count += 1
        self.save(update_fields=['download_count'])
    
    @property
    def file_size(self):
        """Get file size in MB"""
        if self.audio_file:
            try:
                return round(self.audio_file.size / (1024 * 1024), 2)
            except:
                return 0
        return 0
    
    @property
    def file_name(self):
        """Get the original filename"""
        if self.audio_file:
            return os.path.basename(self.audio_file.name)
        return None
    
    @property
    def duration_formatted(self):
        """Return formatted duration string (MM:SS)"""
        if self.duration:
            total_seconds = int(self.duration.total_seconds())
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{minutes}:{seconds:02d}"
        return "0:00"


class Playlist(models.Model):
    """
    Playlist Model
    User-created collections of songs
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='playlists'
    )
    songs = models.ManyToManyField(
        Song, 
        related_name='in_playlists', 
        blank=True
    )
    cover_image = models.ImageField(
        upload_to='playlist_covers/', 
        blank=True, 
        null=True,
        help_text="Custom playlist cover image"
    )
    is_public = models.BooleanField(
        default=False,
        help_text="Make this playlist visible to all users"
    )
    is_collaborative = models.BooleanField(
        default=False,
        help_text="Allow other users to add songs"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Playlist'
        verbose_name_plural = 'Playlists'
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} by {self.user.username}"
    
    @property
    def song_count(self):
        """Returns the number of songs in playlist"""
        return self.songs.count()
    
    @property
    def total_duration(self):
        """Calculate total duration of all songs in playlist"""
        total = timedelta()
        for song in self.songs.all():
            if song.duration:
                total += song.duration
        return total
    
    @property
    def total_duration_formatted(self):
        """Return formatted total duration"""
        total = self.total_duration
        total_seconds = int(total.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"


class Favorite(models.Model):
    """
    User's Favorite Songs
    Stores which songs a user has marked as favorite
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='favorites'
    )
    song = models.ForeignKey(
        Song, 
        on_delete=models.CASCADE, 
        related_name='favorited_by'
    )
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'song')
        ordering = ['-added_at']
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'
        indexes = [
            models.Index(fields=['user', '-added_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} likes {self.song.title}"


class PlayHistory(models.Model):
    """
    Track user's play history
    Records when a user plays a song
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='play_history'
    )
    song = models.ForeignKey(
        Song, 
        on_delete=models.CASCADE, 
        related_name='play_history'
    )
    played_at = models.DateTimeField(auto_now_add=True)
    
    # Optional: Track how much of the song was played
    play_duration = models.DurationField(
        null=True, 
        blank=True,
        help_text="How long the song was played"
    )
    completed = models.BooleanField(
        default=False,
        help_text="Was the song played completely"
    )
    
    class Meta:
        ordering = ['-played_at']
        verbose_name = 'Play History'
        verbose_name_plural = 'Play Histories'
        indexes = [
            models.Index(fields=['user', '-played_at']),
            models.Index(fields=['song', '-played_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} played {self.song.title} at {self.played_at}"


class Comment(models.Model):
    """
    Comments on Songs
    Allow users to comment on songs
    """
    song = models.ForeignKey(
        Song, 
        on_delete=models.CASCADE, 
        related_name='comments'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='comments'
    )
    text = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        indexes = [
            models.Index(fields=['song', '-created_at']),
        ]
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.song.title}"


class Rating(models.Model):
    """
    Song Ratings
    Allow users to rate songs (1-5 stars)
    """
    song = models.ForeignKey(
        Song, 
        on_delete=models.CASCADE, 
        related_name='ratings'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='ratings'
    )
    rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)],
        help_text="Rating from 1 to 5 stars"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'song')
        ordering = ['-created_at']
        verbose_name = 'Rating'
        verbose_name_plural = 'Ratings'
    
    def __str__(self):
        return f"{self.user.username} rated {self.song.title}: {self.rating}/5"