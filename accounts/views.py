from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, AuthenticationForm
from django.contrib import messages
from .forms import RegistrationForm, UserUpdateForm, ProfileUpdateForm, ShippingAddressForm
from .models import UserProfile, ShippingAddress
from orders.models import Order
from django.contrib import messages
from django.core.files.base import ContentFile
import base64
import imghdr




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
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def dashboard_view(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # Create profile if doesn't exist
        user_profile = UserProfile.objects.create(user=request.user)
    
    shipping_addresses = ShippingAddress.objects.filter(user=request.user)
    
    # Get recent orders (handle if orders app not installed)
    recent_orders = []
    try:
        from orders.models import Order
        recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    except:
        pass
    
    context = {
        'profile': user_profile,
        'shipping_addresses': shipping_addresses,
        'recent_orders': recent_orders,
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required
def profile_update_view(request):
    # Get or create profile
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=user_profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=user_profile)
    
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
            messages.error(request, 'Please correct the errors below.')
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
            messages.error(request, 'Please correct the errors below.')
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
            messages.error(request, 'Please correct the errors below.')
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
    

@login_required
def profile_update_view(request):
    # Get or create profile
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=user_profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            # Save user data
            user_form.save()
            
            # Save profile data (except picture)
            user_profile.phone = profile_form.cleaned_data.get('phone', '')
            user_profile.address = profile_form.cleaned_data.get('address', '')
            user_profile.city = profile_form.cleaned_data.get('city', '')
            user_profile.postal_code = profile_form.cleaned_data.get('postal_code', '')
            
            # Handle profile picture removal
            if profile_form.cleaned_data.get('remove_picture'):
                user_profile.profile_picture_base64 = None
                user_profile.profile_picture_format = None
            
            # Handle new profile picture upload
            if 'profile_picture' in request.FILES:
                image_file = request.FILES['profile_picture']
                
                # Validate image
                try:
                    # Check if it's a valid image
                    import io
                    from PIL import Image
                    
                    # Read image data
                    image_data = image_file.read()
                    
                    # Try to open with PIL to validate
                    img = Image.open(io.BytesIO(image_data))
                    img.verify()  # Verify it's a valid image
                    
                    # Reset file pointer
                    image_file.seek(0)
                    
                    # Convert to base64
                    base64_str = base64.b64encode(image_data).decode('utf-8')
                    
                    # Determine format
                    format_str = imghdr.what(None, h=image_data)
                    if not format_str:
                        # Try to get from PIL
                        img = Image.open(io.BytesIO(image_data))
                        format_str = img.format.lower() if img.format else 'jpeg'
                    
                    # Save to profile
                    user_profile.profile_picture_base64 = base64_str
                    user_profile.profile_picture_format = format_str
                    
                    messages.success(request, 'Profile picture uploaded successfully!')
                    
                except Exception as e:
                    messages.error(request, f'Invalid image file: {str(e)}')
            
            # Save profile
            user_profile.save()
            
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=user_profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'has_picture': bool(user_profile.profile_picture_base64)
    }
    return render(request, 'accounts/profile_update.html', context)