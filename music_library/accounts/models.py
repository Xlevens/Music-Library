# ============================================
# accounts/models.py
# Extended User Model
# Author: Laiba Imran
# ============================================

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator


class User(AbstractUser):
    """
    Extended User Model
    Adds additional fields to the default Django User model
    """
    email = models.EmailField(unique=True, blank=False)
    bio = models.TextField(
        max_length=500, 
        blank=True,
        help_text="Tell us about yourself"
    )
    profile_picture = models.ImageField(
        upload_to='profile_pics/', 
        blank=True, 
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'gif']
            )
        ],
        help_text="Upload your profile picture"
    )
    date_of_birth = models.DateField(
        null=True, 
        blank=True,
        help_text="Your date of birth"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_joined']
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.username
    
    @property
    def full_name(self):
        """Returns user's full name or username"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        return self.username
    
    @property
    def total_uploads(self):
        """Returns total number of songs uploaded"""
        return self.uploaded_songs.count()
    
    @property
    def total_playlists(self):
        """Returns total number of playlists created"""
        return self.playlists.count()
    
    @property
    def total_favorites(self):
        """Returns total number of favorite songs"""
        return self.favorites.count()


