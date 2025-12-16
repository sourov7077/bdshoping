"""
Management command to seed database with categories and brands only
Usage: python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from products.models import Category, Brand

class Command(BaseCommand):
    help = 'Seed the database with categories and brands for BD Shopping'
    
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Starting database seeding...'))
        
        # ===== CREATE CATEGORIES =====
        categories_data = [
            {
                'name': 'Electronics',
                'icon': 'tv',
                'description': 'Mobile phones, laptops, cameras, headphones, smartwatches and accessories'
            },
            {
                'name': 'Fashion',
                'icon': 'tshirt',
                'description': 'Clothing, shoes, watches, jewelry, bags and accessories for men, women & kids'
            },
            {
                'name': 'Home & Kitchen',
                'icon': 'home',
                'description': 'Home appliances, furniture, kitchenware, bedding, bath and home decor'
            },
            {
                'name': 'Beauty & Health',
                'icon': 'spa',
                'description': 'Cosmetics, skincare, haircare, perfumes, health supplements and personal care'
            },
            {
                'name': 'Sports & Outdoors',
                'icon': 'futbol',
                'description': 'Sports equipment, fitness gear, outdoor games, camping and adventure'
            },
            {
                'name': 'Books & Stationery',
                'icon': 'book',
                'description': 'Books, notebooks, pens, office supplies, art materials and educational items'
            },
            {
                'name': 'Toys & Games',
                'icon': 'gamepad',
                'description': 'Toys, board games, video games, puzzles, educational toys and collectibles'
            },
            {
                'name': 'Automotive',
                'icon': 'car',
                'description': 'Car accessories, motorcycle parts, tools, maintenance products and auto care'
            },
            {
                'name': 'Groceries',
                'icon': 'shopping-basket',
                'description': 'Food items, beverages, snacks, cooking ingredients and household essentials'
            },
            {
                'name': 'Baby Products',
                'icon': 'baby',
                'description': 'Baby clothing, diapers, toys, feeding accessories, strollers and care products'
            },
        ]
        
        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'slug': slugify(cat_data['name']),
                    'icon': cat_data['icon'],
                    'description': cat_data['description'],
                    'is_active': True
                }
            )
            categories.append(category)
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Created category: {cat_data["name"]}'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠️ Category already exists: {cat_data["name"]}'))
        
        # ===== CREATE BRANDS =====
        brands_data = [
            {'name': 'Samsung', 'description': 'South Korean electronics company'},
            {'name': 'Apple', 'description': 'American technology company'},
            {'name': 'Nike', 'description': 'American sports apparel and footwear'},
            {'name': 'Adidas', 'description': 'German athletic apparel and footwear'},
            {'name': 'Sony', 'description': 'Japanese electronics and entertainment'},
            {'name': 'LG', 'description': 'South Korean electronics company'},
            {'name': 'Xiaomi', 'description': 'Chinese electronics company'},
            {'name': 'HP', 'description': 'American information technology company'},
            {'name': 'Dell', 'description': 'American computer technology company'},
            {'name': 'Lenovo', 'description': 'Chinese technology company'},
            {'name': 'Philips', 'description': 'Dutch electronics company'},
            {'name': 'Panasonic', 'description': 'Japanese electronics company'},
            {'name': 'Canon', 'description': 'Japanese imaging and optical products'},
            {'name': 'Nikon', 'description': 'Japanese optics and imaging products'},
            {'name': 'Puma', 'description': 'German sports apparel and footwear'},
            {'name': 'Reebok', 'description': 'American-inspired fitness brand'},
            {'name': 'Levis', 'description': 'American clothing company'},
            {'name': 'Zara', 'description': 'Spanish fast fashion retailer'},
            {'name': 'H&M', 'description': 'Swedish clothing company'},
            {'name': 'Unilever', 'description': 'British consumer goods company'},
            {'name': 'Nestle', 'description': 'Swiss food and drink company'},
            {'name': 'Pampers', 'description': 'American diaper brand'},
            {'name': 'Huggies', 'description': 'American diaper brand'},
            {'name': 'Mattel', 'description': 'American toy company'},
            {'name': 'LEGO', 'description': 'Danish toy company'},
            {'name': 'Hasbro', 'description': 'American toy company'},
        ]
        
        brands = []
        for brand_data in brands_data:
            brand, created = Brand.objects.get_or_create(
                name=brand_data['name'],
                defaults={
                    'slug': slugify(brand_data['name']),
                    'description': brand_data.get('description', '')
                }
            )
            brands.append(brand)
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Created brand: {brand_data["name"]}'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠️ Brand already exists: {brand_data["name"]}'))
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Database seeding completed successfully!'))
        self.stdout.write(self.style.SUCCESS(f'📊 Created/Updated: {len(categories)} categories, {len(brands)} brands'))
        self.stdout.write(self.style.NOTICE('\n📝 Next steps:'))
        self.stdout.write(self.style.NOTICE('1. Run: python manage.py createsuperuser'))
        self.stdout.write(self.style.NOTICE('2. Login to admin panel: /admin'))
        self.stdout.write(self.style.NOTICE('3. Add products manually with your own images'))