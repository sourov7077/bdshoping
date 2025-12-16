from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product, Category, Brand
from .forms import ProductFilterForm

def product_list(request):
    products = Product.objects.filter(is_active=True)
    
    # Search
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Filtering
    form = ProductFilterForm(request.GET)
    if form.is_valid():
        category = form.cleaned_data.get('category')
        brand = form.cleaned_data.get('brand')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        sort_by = form.cleaned_data.get('sort_by')
        
        if category:
            products = products.filter(category=category)
        if brand:
            products = products.filter(brand=brand)
        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)
        
        # Sorting
        if sort_by == 'price_low':
            products = products.order_by('price')
        elif sort_by == 'price_high':
            products = products.order_by('-price')
        elif sort_by == 'name':
            products = products.order_by('name')
        else:  # newest
            products = products.order_by('-created_at')
    
    # Get categories for sidebar
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
        'brands': brands,
        'form': form,
        'search_query': search_query,
    }
    return render(request, 'products/product_list.html', context)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(pk=pk)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'products/product_detail.html', context)

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(category=category, is_active=True)
    
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'products/category_detail.html', context)
    
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product, Category, Brand
from .forms import ProductFilterForm

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(category=category, is_active=True)
    
    # Get all active categories for sidebar
    all_categories = Category.objects.filter(is_active=True).exclude(id=category.id)
    
    # Apply filters if any
    form = ProductFilterForm(request.GET)
    if form.is_valid():
        brand = form.cleaned_data.get('brand')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        sort_by = form.cleaned_data.get('sort_by')
        
        if brand:
            products = products.filter(brand=brand)
        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)
        
        # Sorting
        if sort_by == 'price_low':
            products = products.order_by('price')
        elif sort_by == 'price_high':
            products = products.order_by('-price')
        elif sort_by == 'name':
            products = products.order_by('name')
        else:  # newest
            products = products.order_by('-created_at')
    
    context = {
        'category': category,
        'products': products,
        'all_categories': all_categories,
        'form': form,
    }
    return render(request, 'products/category_detail.html', context)