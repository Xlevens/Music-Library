# ============================================
# accounts/views.py
# Complete Views for User Authentication
# Author: Laiba Imran
# ============================================

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm, UserUpdateForm


def register(request):
    """
    User Registration View
    Handles new user account creation
    """
    if request.user.is_authenticated:
        return redirect('music:home')
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(
                request, 
                f'Account created successfully for {username}! You can now log in.'
            )
            # Auto-login the user after registration
            login(request, user)
            return redirect('music:home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegisterForm()
    
    context = {'form': form}
    return render(request, 'accounts/register.html', context)


def user_login(request):
    """
    User Login View
    Handles user authentication
    """
    if request.user.is_authenticated:
        return redirect('music:home')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                
                # Redirect to 'next' parameter if exists, otherwise home
                next_url = request.GET.get('next', 'music:home')
                return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    context = {'form': form}
    return render(request, 'accounts/login.html', context)


@login_required
def user_logout(request):
    """
    User Logout View
    Logs out the current user
    """
    username = request.user.username
    logout(request)
    messages.info(request, f'You have been logged out successfully. See you soon, {username}!')
    return redirect('accounts:login')


@login_required
def profile(request):
    """
    User Profile View
    Display and edit user profile information
    """
    if request.method == 'POST':
        form = UserUpdateForm(
            request.POST, 
            request.FILES, 
            instance=request.user
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserUpdateForm(instance=request.user)
    
    # Get user statistics
    context = {
        'form': form,
        'uploaded_songs': request.user.uploaded_songs.count(),
        'playlists': request.user.playlists.count(),
        'favorites': request.user.favorites.count(),
    }
    
    return render(request, 'accounts/profile.html', context)