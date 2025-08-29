from django.urls import path
from . import views

app_name = 'myapp'  # Add namespace

urlpatterns = [
    path('', views.home, name='home'),
    
]