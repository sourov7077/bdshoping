from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from orders.models import Order
from .models import Payment

@login_required
def payment_method(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        
        if payment_method:
            # Create payment record
            payment = Payment.objects.create(
                order=order,
                payment_method=payment_method,
                amount=order.total
            )
            
            # Update order payment method
            order.payment_method = payment_method
            order.save()
            
            if payment_method == 'cod':
                order.payment_status = 'paid'
                order.save()
                messages.success(request, 'Order placed successfully with Cash on Delivery!')
                return redirect('order_detail', order_id=order.id)
            else:
                # Redirect to payment gateway
                return redirect('payment_process', payment_id=payment.id)
    
    return render(request, 'payments/payment_method.html', {'order': order})

@login_required
def payment_process(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, order__user=request.user)
    
    # Here you would integrate with actual payment gateway
    # For demo, we'll simulate successful payment
    if request.method == 'POST':
        payment.status = 'completed'
        payment.transaction_id = f"TXN{payment.id}{payment.order.id}"
        payment.save()
        
        # Update order status
        order = payment.order
        order.payment_status = 'paid'
        order.save()
        
        messages.success(request, 'Payment completed successfully!')
        return redirect('order_detail', order_id=order.id)
    
    return render(request, 'payments/payment_process.html', {'payment': payment})

@login_required
def payment_success(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, order__user=request.user)
    return render(request, 'payments/payment_success.html', {'payment': payment})

@login_required
def payment_failed(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, order__user=request.user)
    return render(request, 'payments/payment_failed.html', {'payment': payment})