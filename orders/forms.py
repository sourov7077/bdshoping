from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['shipping_address', 'shipping_city', 'shipping_postal_code', 'shipping_phone',
                 'billing_address', 'payment_method', 'notes']
        widgets = {
            'shipping_address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'billing_address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class OrderUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status', 'payment_status']