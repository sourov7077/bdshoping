# payments/utils.py
import requests
from django.conf import settings
from django.urls import reverse

def get_sslcommerz_config():
    """SSLCommerz configuration - Sandbox mode for testing"""
    return {
        'store_id': 'testbox',
        'store_pass': 'qwerty',
        'is_sandbox': True,
        'base_url': 'https://sandbox.sslcommerz.com'
    }

def create_sslcommerz_payment(payment, request):
    """Create SSLCommerz payment session"""
    config = get_sslcommerz_config()
    order = payment.order
    
    # Build URLs
    success_url = request.build_absolute_uri(
        reverse('payments:sslcommerz_success', kwargs={'payment_id': payment.id})
    )
    fail_url = request.build_absolute_uri(
        reverse('payments:sslcommerz_fail', kwargs={'payment_id': payment.id})
    )
    cancel_url = request.build_absolute_uri(
        reverse('payments:sslcommerz_cancel', kwargs={'payment_id': payment.id})
    )
    ipn_url = request.build_absolute_uri(reverse('payments:sslcommerz_ipn'))
    
    # Customer info
    customer_name = order.user.get_full_name() or order.user.username
    customer_email = order.user.email
    customer_phone = getattr(order.shipping_address, 'phone', '') if hasattr(order, 'shipping_address') else ''
    
    # Prepare post data
    post_data = {
        'store_id': config['store_id'],
        'store_passwd': config['store_pass'],
        'total_amount': str(payment.amount),
        'currency': 'BDT',
        'tran_id': f"SSL{payment.id}{order.id}",
        'success_url': success_url,
        'fail_url': fail_url,
        'cancel_url': cancel_url,
        'ipn_url': ipn_url,
        'cus_name': customer_name,
        'cus_email': customer_email,
        'cus_add1': 'Dhaka',
        'cus_city': 'Dhaka',
        'cus_postcode': '1200',
        'cus_country': 'Bangladesh',
        'cus_phone': customer_phone or '01700000000',
        'shipping_method': 'NO',
        'product_name': f'Order #{order.id}',
        'product_category': 'General',
        'product_profile': 'general',
        'value_a': str(payment.id),
        'value_b': str(order.id),
        'value_c': customer_email,
    }
    
    try:
        # SSLCommerz API call
        response = requests.post(
            f"{config['base_url']}/gwprocess/v4/api.php",
            data=post_data,
            timeout=30
        )
        
        if response.status_code == 200:
            response_data = response.json()
            
            if response_data.get('status') == 'SUCCESS':
                # Update payment with transaction ID
                payment.transaction_id = response_data.get('tran_id', '')
                payment.payment_details = response_data
                payment.save()
                
                return {
                    'success': True,
                    'redirect_url': response_data['GatewayPageURL'],
                    'session_key': response_data.get('sessionkey'),
                    'transaction_id': response_data.get('tran_id')
                }
            else:
                return {
                    'success': False,
                    'message': response_data.get('failedreason', 'Payment initialization failed')
                }
        else:
            return {
                'success': False,
                'message': f'API Error: {response.status_code}'
            }
            
    except Exception as e:
        return {
            'success': False,
            'message': f'Connection error: {str(e)}'
        }

def validate_sslcommerz_payment(val_id):
    """Validate SSLCommerz payment"""
    config = get_sslcommerz_config()
    
    try:
        verify_url = f"{config['base_url']}/validator/api/validationserverAPI.php"
        params = {
            'val_id': val_id,
            'store_id': config['store_id'],
            'store_passwd': config['store_pass'],
            'format': 'json',
            'v': '1'
        }
        
        response = requests.get(verify_url, params=params, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None