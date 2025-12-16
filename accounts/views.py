from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from .forms import RegistrationForm, LoginForm, UserUpdateForm, ProfileUpdateForm, ShippingAddressForm
from .models import UserProfile, ShippingAddress
from orders.models import Order

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome to BD Shopping.')
            return redirect('home')
    else:
        form = RegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('home')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def dashboard_view(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    shipping_addresses = ShippingAddress.objects.filter(user=request.user)
    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'profile': user_profile,
        'shipping_addresses': shipping_addresses,
        'recent_orders': recent_orders,
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required
def profile_update_view(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, 
                                         instance=request.user.userprofile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('dashboard')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.userprofile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'accounts/profile_update.html', context)

@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('dashboard')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})

@login_required
def shipping_address_view(request):
    addresses = ShippingAddress.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            
            # If this is set as default, unset other defaults
            if address.is_default:
                ShippingAddress.objects.filter(user=request.user, is_default=True).update(is_default=False)
            
            address.save()
            messages.success(request, 'Shipping address added successfully!')
            return redirect('shipping_address')
    else:
        form = ShippingAddressForm()
    
    context = {
        'addresses': addresses,
        'form': form
    }
    return render(request, 'accounts/shipping_address.html', context)

@login_required
def edit_shipping_address(request, id):
    address = get_object_or_404(ShippingAddress, id=id, user=request.user)
    
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST, instance=address)
        if form.is_valid():
            address = form.save(commit=False)
            
            # If this is set as default, unset other defaults
            if address.is_default:
                ShippingAddress.objects.filter(user=request.user, is_default=True).update(is_default=False)
            
            address.save()
            messages.success(request, 'Shipping address updated successfully!')
            return redirect('shipping_address')
    else:
        form = ShippingAddressForm(instance=address)
    
    context = {
        'form': form,
        'address': address
    }
    return render(request, 'accounts/edit_shipping_address.html', context)

@login_required
def delete_shipping_address(request, id):
    address = get_object_or_404(ShippingAddress, id=id, user=request.user)
    address.delete()
    messages.success(request, 'Shipping address deleted successfully!')
    return redirect('shipping_address')