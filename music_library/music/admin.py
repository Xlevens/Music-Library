from django.contrib import admin
from .models import Song, Artist, Genre, Playlist, Favorite

admin.site.register(Song)
admin.site.register(Artist)
admin.site.register(Genre)
admin.site.register(Playlist)
admin.site.register(Favorite)
