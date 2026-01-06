# music/forms.py
# Complete Forms for Cloud-Based Music Library
# Author: Laiba Imran
from django.forms.widgets import FileInput

class MultipleFileInput(FileInput):
    allow_multiple_selected = True


from django import forms
from django.core.exceptions import ValidationError
from .models import Song, Playlist, Artist, Album, Genre, Comment, Rating


class SongUploadForm(forms.ModelForm):
    """
    Song Upload Form
    Allows users to upload songs with metadata
    """
    # Additional fields for creating new artist/album/genre
    artist_name = forms.CharField(
        max_length=200, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new artist name'
        }),
        help_text='Enter artist name if not in the list below'
    )
    
    album_title = forms.CharField(
        max_length=200, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new album title'
        }),
        help_text='Enter album title if not in the list below'
    )
    
    genre_name = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new genre'
        }),
        help_text='Enter genre if not in the list below'
    )
    
    class Meta:
        model = Song
        fields = [
            'title', 'artist', 'album', 'genre', 
            'audio_file', 'duration', 'lyrics',
            'release_year', 'is_public'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter song title'
            }),
            'artist': forms.Select(attrs={'class': 'form-select'}),
            'album': forms.Select(attrs={'class': 'form-select'}),
            'genre': forms.Select(attrs={'class': 'form-select'}),
            'audio_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'audio/*'
            }),
            'duration': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'step': '1'
            }),
            'lyrics': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Enter song lyrics (optional)'
            }),
            'release_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 2024',
                'min': '1900',
                'max': '2100'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        help_texts = {
            'audio_file': 'Supported formats: MP3, WAV, OGG, M4A, FLAC (Max 50MB)',
            'duration': 'Format: HH:MM:SS',
            'is_public': 'Make this song visible to all users',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make these fields optional as user can create new ones
        self.fields['artist'].required = False
        self.fields['album'].required = False
        self.fields['genre'].required = False
        
        # Add empty label
        self.fields['artist'].empty_label = 'Select existing artist or create new'
        self.fields['album'].empty_label = 'Select existing album or create new (optional)'
        self.fields['genre'].empty_label = 'Select existing genre or create new (optional)'
    
    def clean(self):
        cleaned_data = super().clean()
        artist = cleaned_data.get('artist')
        artist_name = cleaned_data.get('artist_name')
        
        # Artist validation - must have either selected or new name
        if not artist and not artist_name:
            raise ValidationError('Please select an artist or enter a new artist name.')
        
        # Create new artist if name provided
        if not artist and artist_name:
            artist, created = Artist.objects.get_or_create(
                name=artist_name.strip()
            )
            cleaned_data['artist'] = artist
        
        # Create new album if title provided
        album = cleaned_data.get('album')
        album_title = cleaned_data.get('album_title')
        if not album and album_title and cleaned_data.get('artist'):
            album, created = Album.objects.get_or_create(
                title=album_title.strip(),
                artist=cleaned_data['artist']
            )
            cleaned_data['album'] = album
        
        # Create new genre if name provided
        genre = cleaned_data.get('genre')
        genre_name = cleaned_data.get('genre_name')
        if not genre and genre_name:
            genre, created = Genre.objects.get_or_create(
                name=genre_name.strip()
            )
            cleaned_data['genre'] = genre
        
        # Validate audio file size (50MB limit)
        audio_file = cleaned_data.get('audio_file')
        if audio_file:
            if audio_file.size > 50 * 1024 * 1024:  # 50MB in bytes
                raise ValidationError('Audio file size cannot exceed 50MB.')
        
        return cleaned_data


class PlaylistForm(forms.ModelForm):
    """
    Playlist Creation/Edit Form
    """
    class Meta:
        model = Playlist
        fields = ['name', 'description', 'cover_image', 'is_public', 'is_collaborative']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter playlist name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your playlist (optional)'
            }),
            'cover_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_collaborative': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        help_texts = {
            'cover_image': 'Upload a custom cover image (optional)',
            'is_public': 'Make this playlist visible to all users',
            'is_collaborative': 'Allow other users to add songs to this playlist',
        }
    
    def clean_cover_image(self):
        """Validate cover image"""
        cover_image = self.cleaned_data.get('cover_image')
        if cover_image:
            # Check file size (5MB limit)
            if cover_image.size > 5 * 1024 * 1024:
                raise ValidationError('Image file size cannot exceed 5MB.')
            
            # Check file type
            valid_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if cover_image.content_type not in valid_types:
                raise ValidationError('Only JPEG, PNG, and GIF images are allowed.')
        
        return cover_image


class SongSearchForm(forms.Form):
    """
    Song Search Form
    Advanced search with multiple filters
    """
    query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search songs, artists, albums...'
        })
    )
    
    genre = forms.ModelChoiceField(
        queryset=Genre.objects.all(),
        required=False,
        empty_label='All Genres',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    artist = forms.ModelChoiceField(
        queryset=Artist.objects.all(),
        required=False,
        empty_label='All Artists',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    album = forms.ModelChoiceField(
        queryset=Album.objects.all(),
        required=False,
        empty_label='All Albums',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    sort_by = forms.ChoiceField(
        choices=[
            ('-upload_date', 'Newest First'),
            ('upload_date', 'Oldest First'),
            ('title', 'Title (A-Z)'),
            ('-title', 'Title (Z-A)'),
            ('-play_count', 'Most Played'),
            ('artist__name', 'Artist (A-Z)'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class CommentForm(forms.ModelForm):
    """
    Comment Form
    Allow users to comment on songs
    """
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write your comment...',
                'maxlength': '1000'
            })
        }
        labels = {
            'text': ''
        }
    
    def clean_text(self):
        """Validate comment text"""
        text = self.cleaned_data.get('text')
        if text:
            text = text.strip()
            if len(text) < 2:
                raise ValidationError('Comment must be at least 2 characters long.')
        return text


class RatingForm(forms.ModelForm):
    """
    Rating Form
    Allow users to rate songs (1-5 stars)
    """
    class Meta:
        model = Rating
        fields = ['rating']
        widgets = {
            'rating': forms.RadioSelect(
                choices=[(i, '★' * i) for i in range(1, 6)]
            )
        }
        labels = {
            'rating': 'Rate this song'
        }


class ArtistForm(forms.ModelForm):
    """
    Artist Creation/Edit Form
    """
    class Meta:
        model = Artist
        fields = ['name', 'bio', 'image', 'country', 'website']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Artist or Band Name'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Artist biography'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Country of origin'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://artist-website.com'
            }),
        }


class AlbumForm(forms.ModelForm):
    """
    Album Creation/Edit Form
    """
    class Meta:
        model = Album
        fields = ['title', 'artist', 'cover_image', 'release_date', 'description', 'record_label']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Album Title'
            }),
            'artist': forms.Select(attrs={'class': 'form-select'}),
            'cover_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'release_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Album description'
            }),
            'record_label': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Record Label'
            }),
        }


class GenreForm(forms.ModelForm):
    """
    Genre Creation/Edit Form
    """
    class Meta:
        model = Genre
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Genre Name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Genre description'
            }),
        }


class BulkUploadForm(forms.Form):
    """
    Bulk Upload Form
    Upload multiple songs at once
    """
    audio_files = forms.FileField(
        widget=MultipleFileInput(attrs={
       
            'multiple': True,
            'class': 'form-control',
            'accept': 'audio/*'
        }),
        help_text='Select multiple audio files to upload'
    )
    
    artist = forms.ModelChoiceField(
        queryset=Artist.objects.all(),
        required=False,
        empty_label='Select Artist',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    artist_name = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Or enter new artist name'
        })
    )
    
    album = forms.ModelChoiceField(
        queryset=Album.objects.all(),
        required=False,
        empty_label='Select Album (optional)',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    genre = forms.ModelChoiceField(
        queryset=Genre.objects.all(),
        required=False,
        empty_label='Select Genre (optional)',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    is_public = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text='Make all uploaded songs public'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        artist = cleaned_data.get('artist')
        artist_name = cleaned_data.get('artist_name')
        
        if not artist and not artist_name:
            raise ValidationError('Please select an artist or enter a new artist name.')
        
        return cleaned_data


class PlaylistAddSongsForm(forms.Form):
    """
    Form to add multiple songs to a playlist
    """
    songs = forms.ModelMultipleChoiceField(
        queryset=Song.objects.filter(is_public=True),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            # Show public songs and user's private songs
            self.fields['songs'].queryset = Song.objects.filter(
                models.Q(is_public=True) | models.Q(uploaded_by=user)
            )


class AdvancedSearchForm(forms.Form):
    """
    Advanced Search Form
    More detailed search options
    """
    title = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Song title'
        })
    )
    
    artist = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Artist name'
        })
    )
    
    album = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Album title'
        })
    )
    
    genre = forms.ModelChoiceField(
        queryset=Genre.objects.all(),
        required=False,
        empty_label='Any Genre',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    year_from = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'From year',
            'min': '1900',
            'max': '2100'
        })
    )
    
    year_to = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'To year',
            'min': '1900',
            'max': '2100'
        })
    )
    
    min_duration = forms.DurationField(
        required=False,
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        }),
        help_text='Minimum duration'
    )
    
    max_duration = forms.DurationField(
        required=False,
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        }),
        help_text='Maximum duration'
    )


# Import models for forms that need it
from django.db import models