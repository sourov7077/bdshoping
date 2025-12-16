from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('method/<int:order_id>/', views.payment_method, name='payment_method'),
    path('process/<int:payment_id>/', views.payment_process, name='payment_process'),
    path('success/<int:payment_id>/', views.payment_success, name='payment_success'),
    path('failed/<int:payment_id>/', views.payment_failed, name='payment_failed'),
    path('cancel/<int:payment_id>/', views.payment_cancel, name='payment_cancel'),
    path('sslcommerz/success/<int:payment_id>/', views.sslcommerz_success, name='sslcommerz_success'),
    path('sslcommerz/fail/<int:payment_id>/', views.sslcommerz_fail, name='sslcommerz_fail'),
    path('sslcommerz/cancel/<int:payment_id>/', views.sslcommerz_cancel, name='sslcommerz_cancel'),
    path('sslcommerz/ipn/', views.sslcommerz_ipn, name='sslcommerz_ipn'),
]