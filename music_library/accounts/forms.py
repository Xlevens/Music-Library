# ============================================
# accounts/forms.py
# Complete Forms for User Authentication
# Author: Laiba Imran
# ============================================

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class UserRegisterForm(UserCreationForm):
    """
    User Registration Form
    Extended registration form with email field
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        }),
        help_text='We will never share your email with anyone.'
    )
    
    first_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name (optional)'
        })
    )
    
    last_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name (optional)'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create a strong password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
        
        # Update help texts
        self.fields['username'].help_text = 'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
        self.fields['password1'].help_text = 'Your password must contain at least 8 characters and cannot be entirely numeric.'
    
    def clean_email(self):
        """Validate that email is unique"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email address is already registered.')
        return email
    
    def clean_username(self):
        """Validate username"""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('This username is already taken.')
        return username


class UserUpdateForm(forms.ModelForm):
    """
    User Profile Update Form
    Allows users to update their profile information
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your email address'
        })
    )
    
    class Meta:
        model = User
        fields = [
            'username', 
            'email', 
            'first_name', 
            'last_name', 
            'bio', 
            'profile_picture', 
            'date_of_birth'
        ]
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last name'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself...'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
        help_texts = {
            'username': 'Required. 150 characters or fewer.',
            'bio': 'Maximum 500 characters.',
            'profile_picture': 'Upload a profile picture (JPG, PNG, GIF)',
            'date_of_birth': 'Your date of birth (optional)',
        }
    
    def clean_email(self):
        """Validate that email is unique (excluding current user)"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('This email address is already in use.')
        return email
    
    def clean_username(self):
        """Validate that username is unique (excluding current user)"""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise ValidationError('This username is already taken.')
        return username
    
    def clean_profile_picture(self):
        """Validate profile picture"""
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            # Check file size (max 5MB)
            if profile_picture.size > 5 * 1024 * 1024:
                raise ValidationError('Image file size cannot exceed 5MB.')
            
            # Check file type
            valid_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if profile_picture.content_type not in valid_types:
                raise ValidationError('Only JPEG, PNG, and GIF images are allowed.')
        
        return profile_picture
    
    def clean_bio(self):
        """Validate bio length"""
        bio = self.cleaned_data.get('bio')
        if bio and len(bio) > 500:
            raise ValidationError('Bio cannot exceed 500 characters.')
        return bio


