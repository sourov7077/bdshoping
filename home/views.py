from django.shortcuts import render
from products.models import Product, Category

def home(request):
    # Get featured products
    featured_products = Product.objects.filter(is_featured=True)[:8]
    
    # Get new arrivals
    new_arrivals = Product.objects.all().order_by('-created_at')[:8]
    
    # Get categories
    categories = Category.objects.all()[:6]
    
    context = {
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
        'categories': categories,
    }
    return render(request, 'home/index.html', context)