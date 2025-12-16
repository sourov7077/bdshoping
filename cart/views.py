from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from products.models import Product
from .models import Cart, CartItem

@login_required
def cart_detail(request):
    """View cart details"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'cart_total': cart.total_price,
        'cart_count': cart.total_items,
    }
    return render(request, 'cart/detail.html', context)

@login_required
def cart_add(request, product_id):
    """Add product to cart"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    # Check stock
    if product.stock < 1:
        messages.error(request, f'Sorry, {product.name} is out of stock!')
        return redirect('product_detail', product_id=product_id)
    
    # Get or create cart
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Add item to cart
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        # If already in cart, increase quantity
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f'{product.name} quantity increased in cart!')
        else:
            messages.warning(request, f'Cannot add more {product.name}. Only {product.stock} available!')
    else:
        messages.success(request, f'{product.name} added to cart!')
    
    # Check if request is AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Product added to cart',
            'cart_count': cart.total_items,
            'cart_total': float(cart.total_price),
        })
    
    # Redirect back to product page or cart
    redirect_to = request.GET.get('next', 'product_detail')
    if redirect_to == 'cart':
        return redirect('cart_detail')
    else:
        return redirect('product_detail', product_id=product_id)

@login_required
def cart_update(request, item_id):
    """Update cart item quantity"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'increase':
            if cart_item.quantity < cart_item.product.stock:
                cart_item.quantity += 1
                cart_item.save()
                messages.success(request, f'{cart_item.product.name} quantity increased!')
            else:
                messages.warning(request, f'Cannot add more {cart_item.product.name}. Stock limited!')
        
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
                messages.success(request, f'{cart_item.product.name} quantity decreased!')
            else:
                cart_item.delete()
                messages.success(request, f'{cart_item.product.name} removed from cart!')
    
    return redirect('cart_detail')

@login_required
def cart_remove(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'{product_name} removed from cart!')
    
    return redirect('cart_detail')

@login_required
def cart_clear(request):
    """Clear all items from cart"""
    cart = get_object_or_404(Cart, user=request.user)
    cart.items.all().delete()
    messages.success(request, 'Cart cleared successfully!')
    
    return redirect('cart_detail')

def cart_summary(request):
    """Get cart summary for AJAX requests"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        return JsonResponse({
            'count': cart.total_items,
            'total': float(cart.total_price),
        })
    return JsonResponse({'count': 0, 'total': 0})
    
@login_required
def cart_add(request, product_id):
    """Add product to cart"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    # Check stock
    if product.stock < 1:
        messages.error(request, f'Sorry, {product.name} is out of stock!')
        return redirect('product_detail', product_id=product_id)
    
    # Get or create cart
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Add item to cart
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        # If already in cart, increase quantity
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f'{product.name} quantity increased in cart!')
        else:
            messages.warning(request, f'Cannot add more {product.name}. Only {product.stock} available!')
    else:
        messages.success(request, f'{product.name} added to cart!')
    
    # Check if request is AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Product added to cart',
            'cart_count': cart.total_items,
            'cart_total': float(cart.total_price),
        })
    
    # Redirect back to product page or cart - FIXED
    redirect_to = request.GET.get('next', '')
    if redirect_to == 'cart':
        return redirect('cart_detail')
    else:
        return redirect('product_detail', product_id=product_id)  # FIXED: product_id instead of pk
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def checkout_view(request):
    """Checkout page"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    
    if not cart_items:
        messages.warning(request, 'Your cart is empty!')
        return redirect('cart_detail')
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'cart/checkout.html', context)
    
@login_required
def checkout_view(request):
    """Simple checkout page"""
    return render(request, 'cart/checkout.html')