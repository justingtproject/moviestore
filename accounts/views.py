from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from .forms import CustomUserCreationForm, CustomErrorList, UserProfileForm, RegionDetectForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import UserProfile, Region
from django.contrib import messages
from django.db.models import F
import math
from django.http import JsonResponse

@login_required
def logout(request):
    auth_logout(request)
    return redirect('home.index')

def login(request):
    template_data = {}
    template_data['title'] = 'Login'
    if request.method == 'GET':
        return render(request, 'accounts/login.html', {'template_data': template_data})
    elif request.method == 'POST':
        user = authenticate(request, username = request.POST['username'], password = request.POST['password'])
        if user is None:
            template_data['error'] = 'The username or password is incorrect.'
            return render(request, 'accounts/login.html', {'template_data': template_data})
        else:
            auth_login(request, user)
            return redirect('home.index')

def signup(request):
    template_data = {}
    template_data['title'] = 'Sign Up'

    if request.method == 'GET':
        template_data['form'] = CustomUserCreationForm()
        return render(request, 'accounts/signup.html', {'template_data': template_data})
    elif request.method == 'POST':
        form = CustomUserCreationForm(request.POST, error_class=CustomErrorList)
        if form.is_valid():
            form.save()
            return redirect('accounts.login')
        else:
            template_data['form'] = form
            return render(request, 'accounts/signup.html', {'template_data': template_data})

@login_required
def orders(request):
    template_data = {}
    template_data['title'] = 'Orders'
    template_data['orders'] = request.user.order_set.all()
    return render(request, 'accounts/orders.html', {'template_data': template_data})

@login_required
def profile(request):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    form = None  # Ensure form is always defined
    if request.method == 'POST':
        if 'region' in request.POST:
            form = UserProfileForm(request.POST, instance=user_profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated.')
                return redirect('profile')
        elif 'latitude' in request.POST and 'longitude' in request.POST:
            lat = float(request.POST['latitude'])
            lng = float(request.POST['longitude'])
            # Find nearest region
            regions = Region.objects.annotate(
                dist=((F('latitude')-lat)*(F('latitude')-lat) + (F('longitude')-lng)*(F('longitude')-lng))
            ).order_by('dist')
            if regions.exists():
                user_profile.region = regions.first()
                user_profile.save()
                messages.success(request, f"Region set to {regions.first().name} by location.")
                return redirect('profile')
            form = UserProfileForm(instance=user_profile)  # fallback for rendering
    else:
        form = UserProfileForm(instance=user_profile)
    detect_form = RegionDetectForm()
    return render(request, 'accounts/profile.html', {'form': form, 'detect_form': detect_form, 'user_profile': user_profile})

@login_required
def profile_json(request):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    region = user_profile.region
    data = {
        'region': {
            'name': region.name if region else None,
            'latitude': region.latitude if region else None,
            'longitude': region.longitude if region else None,
        } if region else None
    }
    return JsonResponse(data)