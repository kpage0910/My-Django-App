from django.urls import path
from . import views

app_name = 'myapp'  # Add namespace

urlpatterns = [
    path('', views.home, name='home'),
    # Customer views
    path('customers/index/', views.CustomerListView.as_view(), name='customer_list_class'),
    path('customers/<str:pk>/', views.CustomerDetailView.as_view(), name='customer_detail'),
    
]