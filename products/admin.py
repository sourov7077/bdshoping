from django.contrib import admin
from django import forms
from .models import Category, Brand, Product, ProductImage
import base64
from PIL import Image

class ProductAdminForm(forms.ModelForm):
    image_upload = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text="Upload product image (will be stored as base64 in database)"
    )
    
    class Meta:
        model = Product
        fields = '__all__'
    
    def save(self, commit=True):
        product = super().save(commit=False)
        
        # Handle image upload
        if 'image_upload' in self.cleaned_data and self.cleaned_data['image_upload']:
            image_file = self.cleaned_data['image_upload']
            
            try:
                # Read image file
                image_data = image_file.read()
                
                # Convert to base64
                base64_str = base64.b64encode(image_data).decode('utf-8')
                
                # Determine format
                format_str = imghdr.what(None, h=image_data)
                if not format_str:
                    format_str = 'jpeg'
                
                product.image_base64 = base64_str
                product.image_format = format_str
            except Exception as e:
                print(f"Error processing image: {e}")
        
        if commit:
            product.save()
        
        return product

class ProductImageInlineForm(forms.ModelForm):
    image_upload = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text="Upload additional product image"
    )
    
    class Meta:
        model = ProductImage
        fields = ['is_default']
    
    def save(self, commit=True):
        product_image = super().save(commit=False)
        
        # Handle image upload
        if 'image_upload' in self.cleaned_data and self.cleaned_data['image_upload']:
            image_file = self.cleaned_data['image_upload']
            
            try:
                # Read image file
                image_data = image_file.read()
                
                # Convert to base64
                base64_str = base64.b64encode(image_data).decode('utf-8')
                
                # Determine format
                format_str = imghdr.what(None, h=image_data)
                if not format_str:
                    format_str = 'jpeg'
                
                product_image.image_base64 = base64_str
                product_image.image_format = format_str
            except Exception as e:
                print(f"Error processing image: {e}")
        
        if commit:
            product_image.save()
        
        return product_image

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    form = ProductImageInlineForm
    extra = 1
    fields = ['image_upload', 'is_default', 'preview']
    readonly_fields = ['preview']
    
    def preview(self, obj):
        if obj.image_base64:
            return f'<img src="{obj.get_image_url()}" style="max-width: 100px; max-height: 100px;">'
        return "No image"
    preview.allow_tags = True

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ('name', 'category', 'price', 'stock', 'is_featured', 'is_active', 'created_at', 'image_preview')
    list_filter = ('category', 'brand', 'is_featured', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    readonly_fields = ('created_at', 'updated_at', 'image_preview')
    fieldsets = (
        ('Product Information', {
            'fields': ('name', 'slug', 'category', 'brand', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'old_price')
        }),
        ('Inventory', {
            'fields': ('stock',)
        }),
        ('Status', {
            'fields': ('is_featured', 'is_active')
        }),
        ('Image', {
            'fields': ('image_upload', 'image_preview')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def image_preview(self, obj):
        if obj.image_base64:
            return f'<img src="{obj.get_image_url()}" style="max-width: 150px; max-height: 150px;">'
        return "No image"
    image_preview.allow_tags = True
    image_preview.short_description = 'Image Preview'