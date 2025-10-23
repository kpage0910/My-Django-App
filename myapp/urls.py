"""
URL Configuration for Django Traders Application
"""
from django.urls import path
from . import views

app_name = 'myapp'

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # Customer URLs
    path('customers/', views.CustomerListView.as_view(), name='customer_list'),
    path('customers/', views.CustomerListView.as_view(), name='customer_list_class'),  # Alias for compatibility
    path('customer/<str:pk>/', views.CustomerDetailView.as_view(), name='customer_detail'),
    path('customer/create/', views.CustomerCreateView.as_view(), name='customer_create'),
    path('customer/<str:pk>/edit/', views.CustomerUpdateView.as_view(), name='customer_edit'),
    
    # Product URLs
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('product/create/', views.ProductCreateView.as_view(), name='product_create'),
    path('product/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_edit'),
    
    # Order URLs
    path('order/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('order/place/', views.OrderCreateView.as_view(), name='place_order'),
    
    # Cart URLs
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', views.add_to_cart_view, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart_view, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart_view, name='clear_cart'),
    path('cart/buy-again/<int:product_id>/', views.buy_again_view, name='buy_again'),
]