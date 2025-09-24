from django.urls import path
from . import views

app_name = 'myapp'  # Add namespace

urlpatterns = [
    path('', views.home, name='home'),
    # Customer views
    path('customers/index/', views.CustomerListView.as_view(), name='customer_list_class'),
    path('customers/<str:pk>/', views.CustomerDetailView.as_view(), name='customer_detail'),

    # Product views
    path('products/index/', views.ProductListView.as_view(), name='product_list'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),

    # Order views
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    
]