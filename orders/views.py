from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
import uuid
from cart.cart import Cart
from .models import Order, OrderItem
from .forms import OrderCreateForm
from products.models import Product

@login_required
def order_create(request):
    cart = Cart(request)
    
    if len(cart) == 0:
        messages.warning(request, 'Your cart is empty!')
        return redirect('product_list')
    
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Calculate totals
                    subtotal = cart.get_total_price()
                    shipping_cost = Decimal('60.00') if subtotal < 1000 else Decimal('0.00')
                    total = subtotal + shipping_cost
                    
                    # Create order
                    order = form.save(commit=False)
                    order.user = request.user
                    order.order_number = str(uuid.uuid4())[:20].replace('-', '').upper()
                    order.subtotal = subtotal
                    order.shipping_cost = shipping_cost
                    order.total = total
                    order.save()
                    
                    # Create order items
                    for item in cart:
                        OrderItem.objects.create(
                            order=order,
                            product=item['product'],
                            product_name=item['product'].name,
                            price=item['price'],
                            quantity=item['quantity'],
                            total=item['total_price']
                        )
                    
                    # Clear the cart
                    cart.clear()
                    
                    messages.success(request, f'Order #{order.order_number} created successfully!')
                    return redirect('order_detail', order_id=order.id)
                    
            except Exception as e:
                messages.error(request, f'Error creating order: {str(e)}')
                return redirect('cart_detail')
    else:
        # Pre-fill form with user data if available
        initial_data = {}
        if request.user.userprofile.phone:
            initial_data['shipping_phone'] = request.user.userprofile.phone
        if request.user.userprofile.address:
            initial_data['shipping_address'] = request.user.userprofile.address
        if request.user.userprofile.city:
            initial_data['shipping_city'] = request.user.userprofile.city
        if request.user.userprofile.postal_code:
            initial_data['shipping_postal_code'] = request.user.userprofile.postal_code
        
        form = OrderCreateForm(initial=initial_data)
    
    context = {
        'form': form,
        'cart': cart,
    }
    return render(request, 'orders/order_create.html', context)

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {
        'order': order,
    }
    return render(request, 'orders/order_detail.html', context)

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'orders/order_history.html', context)