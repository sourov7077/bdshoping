from django.urls import path
from . import views

urlpatterns = [
    path('', views.coupon_list, name='coupon_list'),  # ✅ coupon_list URL যোগ করুন
    path('apply/', views.apply_coupon, name='apply_coupon'),
    path('remove/', views.remove_coupon, name='remove_coupon'),
]