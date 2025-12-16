from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from orders.models import Order, OrderItem
from products.models import Product
from accounts.models import User

@staff_member_required
def admin_dashboard(request):
    """Admin analytics dashboard"""
    
    # Time periods
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Order statistics
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    today_orders = Order.objects.filter(created_at__date=today).count()
    weekly_orders = Order.objects.filter(created_at__gte=week_ago).count()
    
    # Revenue statistics
    total_revenue = Order.objects.aggregate(total=Sum('total'))['total'] or 0
    weekly_revenue = Order.objects.filter(
        created_at__gte=week_ago,
        payment_status='paid'
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # Product statistics
    top_products = Product.objects.annotate(
        total_sold=Sum('orderitem__quantity')
    ).order_by('-total_sold')[:10]
    
    low_stock = Product.objects.filter(stock__lt=10, is_active=True)[:10]
    
    # User statistics
    total_users = User.objects.count()
    new_users_week = User.objects.filter(date_joined__gte=week_ago).count()
    
    # Recent orders
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
    
    context = {
        # Orders
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'today_orders': today_orders,
        'weekly_orders': weekly_orders,
        
        # Revenue
        'total_revenue': total_revenue,
        'weekly_revenue': weekly_revenue,
        
        # Products
        'top_products': top_products,
        'low_stock': low_stock,
        
        # Users
        'total_users': total_users,
        'new_users_week': new_users_week,
        
        # Recent data
        'recent_orders': recent_orders,
        
        # Chart data (simplified)
        'chart_labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        'chart_data': [100, 150, 200, 180, 250, 300, 280],
    }
    
    return render(request, 'analytics/dashboard.html', context)