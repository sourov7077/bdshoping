from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from products.models import Product
from .models import Wishlist, WishlistItem

@login_required
def wishlist_view(request):
    """View user's wishlist"""
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist_items = wishlist.items.select_related('product').all()
    
    context = {
        'wishlist': wishlist,
        'wishlist_items': wishlist_items,
    }
    return render(request, 'wishlist/wishlist.html', context)

@login_required
def add_to_wishlist(request, product_id):
    """Add product to wishlist"""
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    # Check if already in wishlist
    wishlist_item, item_created = WishlistItem.objects.get_or_create(
        wishlist=wishlist,
        product=product
    )
    
    if item_created:
        message = f'{product.name} added to wishlist!'
        added = True
    else:
        message = f'{product.name} is already in your wishlist!'
        added = False
    
    # AJAX response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': message,
            'added': added,
            'wishlist_count': wishlist.item_count,
            'product_id': product_id,
        })
    
    messages.success(request, message)
    return redirect(request.META.get('HTTP_REFERER', 'product_detail'))

@login_required
def remove_from_wishlist(request, item_id):
    """Remove item from wishlist"""
    wishlist_item = get_object_or_404(WishlistItem, id=item_id, wishlist__user=request.user)
    product_name = wishlist_item.product.name
    wishlist_item.delete()
    
    # Get updated wishlist
    wishlist = get_object_or_404(Wishlist, user=request.user)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{product_name} removed from wishlist!',
            'wishlist_count': wishlist.item_count,
        })
    
    messages.success(request, f'{product_name} removed from wishlist!')
    return redirect('wishlist_view')

@login_required
def toggle_wishlist(request, product_id):
    """Toggle product in wishlist"""
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    # Check if in wishlist
    in_wishlist = WishlistItem.objects.filter(wishlist=wishlist, product=product).exists()
    
    if in_wishlist:
        # Remove from wishlist
        WishlistItem.objects.filter(wishlist=wishlist, product=product).delete()
        action = 'removed'
        message = f'{product.name} removed from wishlist'
    else:
        # Add to wishlist
        WishlistItem.objects.create(wishlist=wishlist, product=product)
        action = 'added'
        message = f'{product.name} added to wishlist'
    
    # Get updated count
    wishlist_count = wishlist.item_count
    
    return JsonResponse({
        'success': True,
        'action': action,
        'message': message,
        'wishlist_count': wishlist_count,
        'in_wishlist': not in_wishlist,
    })