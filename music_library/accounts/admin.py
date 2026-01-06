# ============================================
# accounts/admin.py
# Admin Configuration for User Model
# Author: Laiba Imran
# ============================================

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.utils.html import format_html

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """
    Custom User Admin Panel
    Enhanced admin interface for user management
    """
    list_display = [
        'username', 
        'email', 
        'full_name_display',
        'profile_picture_display',
        'is_staff', 
        'is_active',
        'total_uploads',
        'date_joined'
    ]
    
    list_filter = [
        'is_staff', 
        'is_superuser', 
        'is_active', 
        'date_joined',
        'last_login'
    ]
    
    search_fields = [
        'username', 
        'email', 
        'first_name', 
        'last_name'
    ]
    
    readonly_fields = [
        'date_joined', 
        'last_login',
        'created_at',
        'updated_at',
        'total_uploads',
        'total_playlists',
        'total_favorites'
    ]
    
    ordering = ['-date_joined']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': (
                'bio', 
                'profile_picture', 
                'date_of_birth',
                'created_at',
                'updated_at'
            )
        }),
        ('Statistics', {
            'fields': (
                'total_uploads',
                'total_playlists',
                'total_favorites'
            )
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': (
                'email',
                'first_name',
                'last_name',
                'bio',
                'profile_picture',
                'date_of_birth'
            )
        }),
    )
    
    def full_name_display(self, obj):
        """Display full name in admin list"""
        return obj.full_name
    full_name_display.short_description = 'Full Name'
    
    def profile_picture_display(self, obj):
        """Display profile picture thumbnail in admin list"""
        if obj.profile_picture:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius: 50%;" />',
                obj.profile_picture.url
            )
        return format_html(
            '<i class="fas fa-user-circle" style="font-size: 40px; color: #ccc;"></i>'
        )
    profile_picture_display.short_description = 'Picture'
    
    def total_uploads(self, obj):
        """Display total uploads count"""
        return obj.total_uploads
    total_uploads.short_description = 'Songs Uploaded'


# Customize admin site
admin.site.site_header = "Cloud Music Library Admin"
admin.site.site_title = "Music Library Admin"
admin.site.index_title = "Welcome to the Music Library Administration"