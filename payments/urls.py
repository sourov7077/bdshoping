from django.urls import path
from . import views

urlpatterns = [
    path('method/<int:order_id>/', views.payment_method, name='payment_method'),
    path('process/<int:payment_id>/', views.payment_process, name='payment_process'),
    path('success/<int:payment_id>/', views.payment_success, name='payment_success'),
    path('failed/<int:payment_id>/', views.payment_failed, name='payment_failed'),
]