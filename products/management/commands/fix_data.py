from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.core.files import File
import os
from products.models import Category, Brand, Product
from django.conf import settings

class Command(BaseCommand):
    help = 'Fix database with sample products with dummy images'
    
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Creating sample products with safe data...'))
        
        # Get or create categories
        electronics, _ = Category.objects.get_or_create(
            name='Electronics',
            defaults={'slug': 'electronics', 'icon': 'tv'}
        )
        
        fashion, _ = Category.objects.get_or_create(
            name='Fashion',
            defaults={'slug': 'fashion', 'icon': 'tshirt'}
        )
        
        # Get or create brands
        samsung, _ = Brand.objects.get_or_create(
            name='Samsung',
            defaults={'slug': 'samsung'}
        )
        
        nike, _ = Brand.objects.get_or_create(
            name='Nike',
            defaults={'slug': 'nike'}
        )
        
        # Check if products exist, if not create with safe data
        if not Product.objects.filter(name='Samsung Galaxy S23').exists():
            product1 = Product.objects.create(
                name='Samsung Galaxy S23',
                slug='samsung-galaxy-s23',
                category=electronics,
                brand=samsung,
                price=85000,
                old_price=90000,
                description='Latest Samsung smartphone with amazing camera features and powerful performance.',
                stock=50,
                is_featured=True,
                is_active=True
            )
            # Don't add image, will use placeholder
            self.stdout.write(self.style.SUCCESS('✅ Created product: Samsung Galaxy S23'))
        
        if not Product.objects.filter(name='Nike Air Max').exists():
            product2 = Product.objects.create(
                name='Nike Air Max',
                slug='nike-air-max',
                category=fashion,
                brand=nike,
                price=12000,
                description='Comfortable running shoes with air cushioning technology.',
                stock=100,
                is_featured=True,
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS('✅ Created product: Nike Air Max'))
        
        # Create a few more sample products without images
        sample_products = [
            {
                'name': 'Apple iPhone 15',
                'slug': 'apple-iphone-15',
                'category': electronics,
                'price': 95000,
                'description': 'Latest iPhone with advanced camera and A16 chip.'
            },
            {
                'name': 'Sony Headphones',
                'slug': 'sony-headphones',
                'category': electronics,
                'price': 12000,
                'description': 'Noise cancelling headphones with premium sound.'
            },
            {
                'name': 'Adidas Running Shoes',
                'slug': 'adidas-running-shoes',
                'category': fashion,
                'price': 8000,
                'description': 'Lightweight running shoes for daily use.'
            },
        ]
        
        for prod in sample_products:
            if not Product.objects.filter(slug=prod['slug']).exists():
                Product.objects.create(
                    name=prod['name'],
                    slug=prod['slug'],
                    category=prod['category'],
                    price=prod['price'],
                    description=prod['description'],
                    stock=50,
                    is_active=True
                )
                self.stdout.write(self.style.SUCCESS(f'✅ Created product: {prod["name"]}'))
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Sample products created successfully!'))
        self.stdout.write(self.style.NOTICE('Note: No images added. You can add images through admin panel.'))