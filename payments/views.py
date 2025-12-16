# payments/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from orders.models import Order
from .models import Payment
from .utils import create_sslcommerz_payment, validate_sslcommerz_payment
import json

@login_required
def payment_method(request, order_id):
    """Select payment method"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Check if order is already paid
    if order.payment_status == 'paid':
        messages.warning(request, 'This order is already paid!')
        return redirect('order_detail', order_id=order.id)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        
        if payment_method:
            # Create payment record
            payment = Payment.objects.create(
                order=order,
                payment_method=payment_method,
                amount=order.get_total_cost(),
                status='pending'
            )
            
            # Update order with selected payment method
            order.payment_method = payment_method
            order.save()
            
            # Handle different payment methods
            if payment_method == 'cod':
                # Cash on Delivery
                payment.status = 'completed'
                payment.transaction_id = f"COD{payment.id}"
                payment.save()
                
                order.payment_status = 'paid'
                order.save()
                
                messages.success(request, '✅ Order placed successfully with Cash on Delivery!')
                return redirect('order_detail', order_id=order.id)
                
            elif payment_method == 'sslcommerz':
                # Redirect to SSLCommerz
                return redirect('payments:payment_process', payment_id=payment.id)
                
            else:
                # For other methods (bkash, nagad, etc.) - show manual instructions
                payment.status = 'pending'
                payment.save()
                
                messages.info(request, f'Please complete your {payment_method} payment')
                return redirect('payments:payment_process', payment_id=payment.id)
    
    # Available payment methods
    payment_methods = [
        {'code': 'cod', 'name': 'Cash on Delivery', 'icon': '💰', 'description': 'Pay when you receive the product'},
        {'code': 'sslcommerz', 'name': 'Online Payment', 'icon': '💳', 'description': 'Pay with Card/Bank/Mobile Banking'},
        {'code': 'bkash', 'name': 'bKash', 'icon': '📱', 'description': 'Pay via bKash mobile banking'},
        {'code': 'nagad', 'name': 'Nagad', 'icon': '📲', 'description': 'Pay via Nagad mobile banking'},
    ]
    
    return render(request, 'payments/payment_method.html', {
        'order': order,
        'payment_methods': payment_methods
    })

@login_required
def payment_process(request, payment_id):
    """Process payment based on method"""
    payment = get_object_or_404(Payment, id=payment_id, order__user=request.user)
    order = payment.order
    
    if payment.status == 'completed':
        messages.info(request, 'Payment already completed!')
        return redirect('order_detail', order_id=order.id)
    
    context = {
        'payment': payment,
        'order': order,
    }
    
    # Handle different payment methods
    if payment.payment_method == 'sslcommerz':
        # Initialize SSLCommerz payment
        result = create_sslcommerz_payment(payment, request)
        
        if result['success']:
            # Redirect to SSLCommerz gateway
            return redirect(result['redirect_url'])
        else:
            messages.error(request, f"Payment error: {result['message']}")
            return render(request, 'payments/payment_error.html', context)
    
    elif payment.payment_method in ['bkash', 'nagad', 'rocket']:
        # Show manual payment instructions
        context['instructions'] = get_mobile_payment_instructions(payment)
        return render(request, 'payments/manual_payment.html', context)
    
    else:
        return render(request, 'payments/payment_process.html', context)

def get_mobile_payment_instructions(payment):
    """Get instructions for mobile banking payments"""
    instructions = {
        'bkash': [
            "Dial *247#",
            "Select 'Send Money'",
            "Enter Merchant Number: 017XXXXXXXX",
            f"Enter Amount: {payment.amount} BDT",
            f"Enter Reference: Order #{payment.order.id}",
            "Enter your bKash PIN",
            "Take screenshot of success message",
            "Submit screenshot in order details"
        ],
        'nagad': [
            "Open Nagad App",
            "Go to 'Send Money'",
            "Enter Merchant Number: 013XXXXXXXX",
            f"Enter Amount: {payment.amount} BDT",
            f"Enter Reference: Order #{payment.order.id}",
            "Enter your Nagad PIN",
            "Take screenshot of transaction",
            "Submit screenshot in order details"
        ],
    }
    return instructions.get(payment.payment_method, [])

# SSLCommerz Callback Views
@csrf_exempt
def sslcommerz_success(request, payment_id):
    """Handle SSLCommerz success callback"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    # Get POST data from SSLCommerz
    status = request.POST.get('status')
    val_id = request.POST.get('val_id')
    tran_id = request.POST.get('tran_id')
    
    if status == 'VALID':
        # Validate payment
        validation_data = validate_sslcommerz_payment(val_id)
        
        if validation_data and validation_data.get('status') == 'VALID':
            # Payment successful
            payment.status = 'completed'
            payment.transaction_id = tran_id
            payment.payment_details = validation_data
            payment.save()
            
            # Update order
            order = payment.order
            order.payment_status = 'paid'
            order.save()
            
            messages.success(request, '✅ Payment completed successfully!')
            return redirect('order_detail', order_id=order.id)
    
    # If validation fails
    payment.status = 'failed'
    payment.save()
    
    messages.error(request, 'Payment validation failed!')
    return redirect('payments:payment_failed', payment_id=payment.id)

@csrf_exempt
def sslcommerz_fail(request, payment_id):
    """Handle SSLCommerz fail callback"""
    payment = get_object_or_404(Payment, id=payment_id)
    payment.status = 'failed'
    payment.save()
    
    messages.error(request, '❌ Payment failed! Please try again.')
    return redirect('payments:payment_method', order_id=payment.order.id)

@csrf_exempt
def sslcommerz_cancel(request, payment_id):
    """Handle SSLCommerz cancel callback"""
    payment = get_object_or_404(Payment, id=payment_id)
    payment.status = 'cancelled'
    payment.save()
    
    messages.warning(request, 'Payment cancelled by user.')
    return redirect('payments:payment_method', order_id=payment.order.id)

@csrf_exempt
def sslcommerz_ipn(request):
    """Instant Payment Notification (IPN) from SSLCommerz"""
    if request.method == 'POST':
        data = request.POST.dict()
        
        # Extract payment info
        val_id = data.get('val_id')
        tran_id = data.get('tran_id')
        status = data.get('status')
        
        if status == 'VALID' and val_id:
            # Find payment by transaction ID
            try:
                payment = Payment.objects.get(transaction_id=tran_id)
                
                # Validate payment
                validation_data = validate_sslcommerz_payment(val_id)
                
                if validation_data and validation_data.get('status') == 'VALID':
                    payment.status = 'completed'
                    payment.payment_details = validation_data
                    payment.save()
                    
                    # Update order
                    order = payment.order
                    order.payment_status = 'paid'
                    order.save()
            
            except Payment.DoesNotExist:
                pass
        
        return HttpResponse("IPN received", status=200)
    
    return HttpResponse("Invalid request", status=400)

@login_required
def payment_success(request, payment_id):
    """Payment success page"""
    payment = get_object_or_404(Payment, id=payment_id, order__user=request.user)
    return render(request, 'payments/payment_success.html', {'payment': payment})

@login_required
def payment_failed(request, payment_id):
    """Payment failed page"""
    payment = get_object_or_404(Payment, id=payment_id, order__user=request.user)
    return render(request, 'payments/payment_failed.html', {'payment': payment})

@login_required
def payment_cancel(request, payment_id):
    """Payment cancel page"""
    payment = get_object_or_404(Payment, id=payment_id, order__user=request.user)
    return render(request, 'payments/payment_cancel.html', {'payment': payment})