from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product', 'product_name', 'price', 'quantity', 'total')
    can_delete = False
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'total', 'status', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('order_number', 'user__username', 'shipping_phone')
    readonly_fields = ('order_number', 'user', 'subtotal', 'shipping_cost', 
                      'discount', 'total', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'payment_status')
        }),
        ('Shipping Details', {
            'fields': ('shipping_address', 'shipping_city', 'shipping_postal_code', 'shipping_phone')
        }),
        ('Billing Details', {
            'fields': ('billing_address',)
        }),
        ('Financial Information', {
            'fields': ('subtotal', 'shipping_cost', 'discount', 'total')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )