from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import Coupon
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Coupon
from django.utils import timezone

@login_required
def coupon_list(request):
    """View all active coupons"""
    now = timezone.now()
    
    # Get active coupons
    coupons = Coupon.objects.filter(
        is_active=True,
        valid_from__lte=now,
        valid_to__gte=now
    ).order_by('-valid_to')
    
    context = {
        'coupons': coupons,
    }
    return render(request, 'coupons/coupon_list.html', context)

# ... বাকি views (apply_coupon, remove_coupon) থাকবে
@login_required
def apply_coupon(request):
    """Apply coupon to cart"""
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code', '').strip()
        
        if not coupon_code:
            return JsonResponse({'success': False, 'message': 'Please enter coupon code'})
        
        try:
            coupon = Coupon.objects.get(code=coupon_code.upper())
            
            # Get cart total from session or database
            cart_total = request.session.get('cart_total', 0)
            
            if coupon.is_valid():
                discount = coupon.calculate_discount(cart_total)
                
                # Save coupon in session
                request.session['applied_coupon'] = {
                    'code': coupon.code,
                    'discount': float(discount),
                    'type': coupon.discount_type,
                    'value': float(coupon.discount_value)
                }
                
                return JsonResponse({
                    'success': True,
                    'message': 'Coupon applied successfully!',
                    'discount': discount,
                    'new_total': cart_total - discount
                })
            else:
                return JsonResponse({'success': False, 'message': 'Coupon is not valid or expired'})
                
        except Coupon.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid coupon code'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
def remove_coupon(request):
    """Remove applied coupon"""
    if 'applied_coupon' in request.session:
        del request.session['applied_coupon']
    
    return JsonResponse({'success': True, 'message': 'Coupon removed'})