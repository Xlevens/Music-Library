# music/urls.py
# Complete URL Configuration for Music App
# Author: Laiba Imran

from django.urls import path
from . import views

app_name = 'music'

urlpatterns = [
    # ============================================
    # HOME AND DASHBOARD
    # ============================================
    path('', views.home, name='home'),
    
    # ============================================
    # SONG URLS
    # ============================================
    path('songs/', views.song_list, name='song_list'),
    path('songs/<int:pk>/', views.song_detail, name='song_detail'),
    path('songs/upload/', views.upload_song, name='upload_song'),
    path('songs/<int:pk>/edit/', views.edit_song, name='edit_song'),
    path('songs/<int:pk>/delete/', views.delete_song, name='delete_song'),
    path('songs/<int:pk>/play/', views.play_song, name='play_song'),
    path('songs/<int:pk>/download/', views.download_song, name='download_song'),
    
    # ============================================
    # SEARCH
    # ============================================
    path('search/', views.search, name='search'),
    
    # ============================================
    # PLAYLIST URLS
    # ============================================
    path('playlists/', views.playlist_list, name='playlist_list'),
    path('playlists/<int:pk>/', views.playlist_detail, name='playlist_detail'),
    path('playlists/create/', views.create_playlist, name='create_playlist'),
    path('playlists/<int:pk>/edit/', views.edit_playlist, name='edit_playlist'),
    path('playlists/<int:pk>/delete/', views.delete_playlist, name='delete_playlist'),
    path('playlists/add/<int:song_pk>/', views.add_to_playlist, name='add_to_playlist'),
    path('playlists/<int:playlist_pk>/remove/<int:song_pk>/', views.remove_from_playlist, name='remove_from_playlist'),
    
    # ============================================
    # FAVORITE URLS
    # ============================================
    path('favorites/', views.favorites, name='favorites'),
    path('favorites/toggle/<int:song_pk>/', views.toggle_favorite, name='toggle_favorite'),
    
    # ============================================
    # ARTIST AND ALBUM URLS
    # ============================================
    path('artists/', views.artist_list, name='artist_list'),
    path('artists/<int:pk>/', views.artist_detail, name='artist_detail'),
    path('albums/<int:pk>/', views.album_detail, name='album_detail'),
    
    # ============================================
    # COMMENT AND RATING URLS
    # ============================================
    path('songs/<int:song_pk>/comment/', views.add_comment, name='add_comment'),
    path('songs/<int:song_pk>/rate/', views.add_rating, name='add_rating'),
    
    # ============================================
    # HISTORY AND STATS URLS
    # ============================================
    path('history/', views.play_history, name='play_history'),
    path('stats/', views.user_stats, name='user_stats'),
]