# views.py 
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.views import View
from django.db.models import Q, Sum, Count, Avg, F, FloatField, Value, ExpressionWrapper
from django.db.models.functions import TruncYear, TruncMonth, Coalesce
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import JsonResponse
from datetime import datetime, date, timedelta
from decimal import Decimal
import calendar
import json

from .models import (
    Customers, Products, Categories, Orders, OrderDetails, 
    Suppliers, Employees, Shippers
)
from .forms import CustomerForm, OrderForm, ProductForm
from .cart_utils import (
    get_cart, add_to_cart, remove_from_cart, 
    clear_cart, get_cart_items, validate_cart
)
from .recommendation_utils import get_product_recommendations

# Custom mixin for session-based authentication
class SessionLoginRequiredMixin:
    """
    Mixin that checks for session-based authentication.
    Redirects to login if user_id is not in session.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('user_id'):
            messages.warning(request, 'Please log in to access this page.')
            return redirect('myapp:login')
        return super().dispatch(request, *args, **kwargs)

def convert_to_json_safe(data):
    """Convert QuerySet data to JSON-safe format"""
    result = []
    for item in data:
        safe_item = {}
        for key, value in item.items():
            if isinstance(value, Decimal):
                safe_item[key] = float(value)
            elif value is None:
                safe_item[key] = 0
            else:
                safe_item[key] = value
        result.append(safe_item)
    return result

def home(request):
    """
    Function-based view for the home page
    """
    timeNow = datetime.today().strftime("%A %B %d, %Y")
    
    return render(
        request=request,
        template_name="myapp/home.html",
        context={
            "today": timeNow,
            "title": "Django Traders 2.0"
        },
    )


# ====================== CUSTOMER VIEWS ======================

class CustomerListView(SessionLoginRequiredMixin, ListView):
    """
    Class-based view for displaying a list of customers
    """
    model = Customers
    template_name = 'myapp/customer_list.html'
    context_object_name = 'customers'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = Customers.objects.all()
        
        contact_filter = self.request.GET.get('contact', '')
        contact_title_filter = self.request.GET.get('contact_title', '')
        contact_address_filter = self.request.GET.get('address', '')
        city_filter = self.request.GET.get('city', '')
        country_filter = self.request.GET.get('country', '')
        region_filter = self.request.GET.get('region', '')
        
        if contact_filter:
            queryset = queryset.filter(contact_name__icontains=contact_filter)
            
        if contact_title_filter:
            queryset = queryset.filter(contact_title__icontains=contact_title_filter)

        if contact_address_filter:
            queryset = queryset.filter(address__icontains=contact_address_filter)
            
        if city_filter:
            queryset = queryset.filter(city__icontains=city_filter)
            
        if country_filter:
            queryset = queryset.filter(country__icontains=country_filter)
            
        if region_filter:
            queryset = queryset.filter(region__icontains=region_filter)
        
        sort_by = self.request.GET.get('sort', 'company_name')
        if sort_by:
            queryset = queryset.order_by(sort_by)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['contact_filter'] = self.request.GET.get('contact', '')
        context['contact_title_filter'] = self.request.GET.get('contact_title', '')
        context['address_filter'] = self.request.GET.get('address', '') 
        context['city_filter'] = self.request.GET.get('city', '')
        context['country_filter'] = self.request.GET.get('country', '')
        context['region_filter'] = self.request.GET.get('region', '')
        context['current_sort'] = self.request.GET.get('sort', 'company_name')
        context['title'] = 'Customer Management - Django Traders'

        if context['is_paginated']:
            page_obj = context['page_obj']
            context['start_index'] = (page_obj.number - 1) * self.paginate_by
        else:
            context['start_index'] = 0
            
        return context


class CustomerDetailView(DetailView):
    """
    Class-based view for displaying individual customer details
    """
    model = Customers
    template_name = 'myapp/customer_detail.html'
    context_object_name = 'customer'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Customer Details: {self.object.company_name}'
        
        # Add customer's orders to context, sorted by most recent first (newest at top)
        context['orders'] = Orders.objects.filter(
            customer=self.object
        ).select_related('ship_via', 'employee').order_by('-order_id', '-order_date')
        
        return context


class CustomerCreateView(CreateView):
    """
    Class-based view for creating new customers
    """
    model = Customers
    form_class = CustomerForm
    template_name = 'myapp/customer_form.html'
    
    def get_success_url(self):
        return reverse_lazy('myapp:customer_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        # Auto-generate customer ID
        import string
        import random
        
        # Generate a unique 5-character alphanumeric customer ID
        while True:
            new_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            if not Customers.objects.filter(customer_id=new_id).exists():
                form.instance.customer_id = new_id
                break
        
        messages.success(self.request, f'Customer "{form.instance.company_name}" has been created successfully with ID: {new_id}!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Customer'
        context['submit_text'] = 'Create Customer'
        return context


class CustomerUpdateView(UpdateView):
    """
    Class-based view for updating existing customers
    """
    model = Customers
    form_class = CustomerForm
    template_name = 'myapp/customer_form.html'
    
    def get_success_url(self):
        return reverse_lazy('myapp:customer_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, f'Customer "{form.instance.company_name}" has been updated successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Customer: {self.object.company_name}'
        context['submit_text'] = 'Update Customer'
        return context


# ====================== PRODUCT VIEWS ======================

class ProductListView(SessionLoginRequiredMixin, ListView):
    """
    Class-based view for displaying a list of products
    """
    model = Products
    template_name = 'myapp/product_list.html'
    context_object_name = 'products'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = Products.objects.select_related('category').all()
        
        product_name_filter = self.request.GET.get('product_name', '')
        category_filter = self.request.GET.get('category', '')
        supplier_filter = self.request.GET.get('supplier', '')
        discontinued_filter = self.request.GET.get('discontinued', '')
        
        if product_name_filter:
            queryset = queryset.filter(product_name__icontains=product_name_filter)
            
        if category_filter:
            queryset = queryset.filter(category_id=category_filter)

        if supplier_filter:
            queryset = queryset.filter(supplier_id=supplier_filter)
            
        if discontinued_filter:
            if discontinued_filter.lower() in ['true', '1', 'yes', 'discontinued']:
                queryset = queryset.filter(discontinued=1)
            elif discontinued_filter.lower() in ['false', '0', 'no', 'active']:
                queryset = queryset.filter(discontinued=0)
        
        sort_by = self.request.GET.get('sort', 'product_name')
        if sort_by:
            if sort_by == 'category':
                sort_by = 'category__category_name'
            elif sort_by == '-category':
                sort_by = '-category__category_name'
            
            queryset = queryset.order_by(sort_by)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['product_name_filter'] = self.request.GET.get('product_name', '')
        context['category_filter'] = self.request.GET.get('category', '')
        context['supplier_filter'] = self.request.GET.get('supplier', '')
        context['discontinued_filter'] = self.request.GET.get('discontinued', '')
        context['current_sort'] = self.request.GET.get('sort', 'product_name')
        context['title'] = 'Product Management - Django Traders'
        context['categories'] = Categories.objects.all().order_by('category_name')
        context['suppliers'] = Suppliers.objects.all().order_by('company_name')

        if context['is_paginated']:
            page_obj = context['page_obj']
            context['start_index'] = (page_obj.number - 1) * self.paginate_by
        else:
            context['start_index'] = 0
            
        return context


class ProductDetailView(DetailView):
    """
    Class-based view for displaying individual product details
    """
    model = Products
    template_name = 'myapp/product_detail.html'
    context_object_name = 'product'
    
    def get_queryset(self):
        return Products.objects.select_related('category')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Product Details: {self.object.product_name}'
        
        # Get customers who have purchased this product
        from django.db.models import Count, Sum
        
        customer_purchases = OrderDetails.objects.filter(
            product=self.object
        ).values(
            'order__customer__customer_id',
            'order__customer__company_name',
            'order__customer__contact_name'
        ).annotate(
            order_count=Count('order_id', distinct=True),
            total_quantity=Sum('quantity')
        ).order_by('-total_quantity')
        
        context['customer_purchases'] = customer_purchases
        
        return context
    
class ProductCreateView(CreateView):
    """
    Class-based view for creating new products
    """
    model = Products
    form_class = ProductForm
    template_name = 'myapp/product_form.html'
    
    def get_success_url(self):
        return reverse_lazy('myapp:product_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        # Automatically assign the next available product_id
        from django.db import models
        max_id = Products.objects.aggregate(models.Max('product_id'))['product_id__max'] or 0
        form.instance.product_id = max_id + 1
        messages.success(self.request, f'Product "{form.instance.product_name}" has been created successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Product'
        context['submit_text'] = 'Create Product'
        return context


class ProductUpdateView(UpdateView):
    """
    Class-based view for updating existing products
    """
    model = Products
    form_class = ProductForm
    template_name = 'myapp/product_form.html'
    
    def get_success_url(self):
        return reverse_lazy('myapp:product_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, f'Product "{form.instance.product_name}" has been updated successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Product: {self.object.product_name}'
        context['submit_text'] = 'Update Product'
        return context


# ====================== ORDER VIEWS ======================

class OrderDetailView(DetailView):
    """
    View to display order details
    """
    model = Orders
    template_name = 'myapp/order_detail.html'
    context_object_name = 'order'
    
    def get_queryset(self):
        return Orders.objects.select_related('customer', 'employee', 'ship_via')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Order Details: #{self.object.order_id}'
        
        order_details = OrderDetails.objects.filter(
            order=self.object
        ).select_related('product', 'product__category')
        
        context['order_details'] = order_details
        
        # Calculate order totals
        subtotal = 0
        total_items = 0
        
        for detail in order_details:
            subtotal += detail.line_total
            total_items += detail.quantity
        
        context['subtotal'] = subtotal
        context['total_items'] = total_items
        context['total'] = subtotal + (self.object.freight or 0)
        
        return context


class OrderCreateView(CreateView):
    """
    View for creating new orders with shopping cart integration
    NO LOGIN REQUIRED - Customer is selected from dropdown
    """
    model = Orders
    form_class = OrderForm
    template_name = 'myapp/order_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        """
        Validate and clean cart
        """
        # Validate cart - remove discontinued products
        removed_products = validate_cart(request)
        if removed_products:
            messages.warning(
                request,
                f"The following discontinued products were removed from your cart: {', '.join(removed_products)}"
            )
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_initial(self):
        """
        Provide default data to the form
        """
        initial = super().get_initial()
        initial['order_date'] = date.today()
        initial['required_date'] = date.today() + timedelta(days=21)
        initial['freight'] = Decimal('0.00')
        
        return initial
    
    def get_context_data(self, **kwargs):
        """
        Add cart items and customers to context
        """
        context = super().get_context_data(**kwargs)
        context['title'] = 'Place New Order'
        
        # Get all customers for dropdown
        context['customers'] = Customers.objects.all().order_by('company_name')
        
        # Get cart items for display
        cart_data = get_cart_items(self.request)
        context['cart_items'] = cart_data['items']
        context['cart_total'] = cart_data['total']
        context['cart_count'] = cart_data['count']
        
        # Get all products for dropdown (non-discontinued only)
        context['products'] = Products.objects.filter(
            discontinued=0
        ).select_related('category').order_by('product_name')
        
        # Get employees and shippers for dropdowns
        context['employees'] = Employees.objects.all().order_by('last_name', 'first_name')
        context['shippers'] = Shippers.objects.all().order_by('company_name')
        
        return context
    
    def form_valid(self, form):
        """
        Save the order and order details
        """
        # Get the selected customer ID from POST data
        customer_id = self.request.POST.get('customer')
        
        if not customer_id:
            messages.error(self.request, 'Please select a customer for this order.')
            return self.form_invalid(form)
        
        try:
            customer = Customers.objects.get(customer_id=customer_id)
        except Customers.DoesNotExist:
            messages.error(self.request, 'Invalid customer selected.')
            return self.form_invalid(form)
        
        # Get cart items
        cart_data = get_cart_items(self.request)
        
        if not cart_data['items']:
            messages.error(self.request, 'Your cart is empty. Please add products before placing an order.')
            return self.form_invalid(form)
        
        try:
            with transaction.atomic():
                # Set customer and order date
                form.instance.customer = customer
                form.instance.order_date = date.today()
                
                # Save the order
                self.object = form.save()
                
                # Calculate total items in cart for volume discount
                total_items = sum(item['quantity'] for item in cart_data['items'])
                
                # Determine discount based on order volume
                # 0% for orders < 10 items
                # 5% for orders 10-24 items
                # 10% for orders 25-49 items
                # 15% for orders 50+ items
                if total_items >= 50:
                    base_discount = 0.15
                elif total_items >= 25:
                    base_discount = 0.10
                elif total_items >= 10:
                    base_discount = 0.05
                else:
                    base_discount = 0.00
                
                # Create order details from cart items with calculated discount
                for item in cart_data['items']:
                    # Apply additional 5% discount if quantity of single product >= 10
                    item_discount = base_discount
                    if item['quantity'] >= 10:
                        item_discount = min(base_discount + 0.05, 0.20)  # Max 20% discount
                    
                    OrderDetails.objects.create(
                        order=self.object,
                        product=item['product'],
                        unit_price=item['product'].unit_price,
                        quantity=item['quantity'],
                        discount=item_discount
                    )
                
                # Clear the cart after successful order
                clear_cart(self.request)
                
                # Create success message with discount info
                if base_discount > 0:
                    discount_msg = f' A {int(base_discount * 100)}% volume discount has been applied!'
                else:
                    discount_msg = ''
                
                messages.success(
                    self.request,
                    f'Order #{self.object.order_id} created successfully for {customer.company_name}!{discount_msg}'
                )
                
                return redirect(self.get_success_url())
                
        except Exception as e:
            messages.error(self.request, f'Error creating order: {str(e)}')
            return self.form_invalid(form)
    
    def get_success_url(self):
        """
        Redirect to customer detail page after order creation
        """
        return reverse('myapp:customer_detail', kwargs={'pk': self.object.customer.customer_id})


# ====================== CART VIEWS ======================

def add_to_cart_view(request, product_id):
    """
    Add a product to the shopping cart
    """
    if request.method == 'POST':
        try:
            product = get_object_or_404(Products, product_id=product_id)
            
            # Check if product is discontinued
            if product.discontinued == 1:
                messages.error(request, f'{product.product_name} is discontinued and cannot be added to cart.')
            else:
                quantity = int(request.POST.get('quantity', 1))
                add_to_cart(request, product_id, quantity)
                messages.success(request, f'{product.product_name} has been added to your cart.')
            
        except Products.DoesNotExist:
            messages.error(request, 'Product not found.')
        except ValueError:
            messages.error(request, 'Invalid quantity.')
    
    # Redirect back to the referring page or product list
    next_url = request.POST.get('next', request.META.get('HTTP_REFERER', reverse('myapp:product_list')))
    return redirect(next_url)


def remove_from_cart_view(request, product_id):
    """
    Remove a product from the shopping cart
    """
    try:
        product = get_object_or_404(Products, product_id=product_id)
        remove_from_cart(request, product_id)
        messages.success(request, f'{product.product_name} has been removed from your cart.')
    except Products.DoesNotExist:
        messages.error(request, 'Product not found.')
    
    # Redirect back to cart view
    return redirect('myapp:cart_view')


def cart_view(request):
    """
    Display the shopping cart with option to proceed to checkout
    """
    cart_data = get_cart_items(request)
    
    context = {
        'title': 'Shopping Cart',
        'cart_items': cart_data['items'],
        'cart_total': cart_data['total'],
        'cart_count': cart_data['count']
    }
    
    return render(request, 'myapp/cart.html', context)


def clear_cart_view(request):
    """
    Clear all items from the cart
    """
    clear_cart(request)
    messages.success(request, 'Your cart has been cleared.')
    return redirect('myapp:cart_view')


def buy_again_view(request, product_id):
    """
    Quick "Buy Again" functionality - adds product to cart and redirects to order form
    """
    try:
        product = get_object_or_404(Products, product_id=product_id)
        
        # Check if product is discontinued
        if product.discontinued == 1:
            messages.error(request, f'{product.product_name} is discontinued and cannot be ordered.')
            return redirect('myapp:product_detail', pk=product_id)
        
        # Add product to cart with quantity 1
        add_to_cart(request, product_id, 1)
        messages.success(request, f'{product.product_name} has been added to your cart.')
        
        # Redirect to place order page
        return redirect('myapp:place_order')
        
    except Products.DoesNotExist:
        messages.error(request, 'Product not found.')
        return redirect('myapp:product_list')


# ====================== AUTHENTICATION VIEWS ======================

class CustomerLoginView(View):
    """
    Custom login view for customers and employees/managers
    """
    template_name = 'myapp/login.html'
    
    def get(self, request):
        """Display login form"""
        # Redirect if already logged in
        if request.session.get('user_id'):
            if request.session.get('user_type') == 'customer':
                return redirect('myapp:customer_dashboard')
            elif request.session.get('user_type') == 'employee':
                return redirect('myapp:manager_dashboard')
        
        return render(request, self.template_name)
    
    def post(self, request):
        """Handle login form submission"""
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user_type = request.POST.get('user_type', 'customer')
        
        if not username or not password:
            messages.error(request, 'Please provide both username and password.')
            return render(request, self.template_name)
        
        # Authenticate based on user type
        user = authenticate(request, username=username, password=password)
        
        if user:
            # Set session variables
            if isinstance(user, Customers):
                request.session['user_id'] = user.customer_id
                request.session['user_type'] = 'customer'
                request.session['user_name'] = user.company_name
                messages.success(request, f'Welcome back, {user.company_name}!')
                return redirect('myapp:customer_dashboard')
            
            elif isinstance(user, Employees):
                request.session['user_id'] = user.employee_id
                request.session['user_type'] = 'employee'
                request.session['user_name'] = f'{user.first_name} {user.last_name}'
                messages.success(request, f'Welcome, {user.first_name}!')
                return redirect('myapp:manager_dashboard')
        
        # Authentication failed
        messages.error(request, 'Invalid credentials. Please try again.')
        return render(request, self.template_name)


def logout_view(request):
    """
    Logout view - clears session and redirects to home
    """
    user_name = request.session.get('user_name', 'User')
    
    # Clear all session data
    request.session.flush()
    
    messages.success(request, f'Goodbye, {user_name}! You have been logged out.')
    return redirect('myapp:home')


# ====================== DASHBOARD VIEWS ======================

class CustomerDashboardView(TemplateView):
    """
    Customer dashboard showing personal sales analytics and trends
    Requirement 1: Customer Sales Analysis (40%)
    """
    template_name = 'myapp/customer_dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Check if customer is logged in"""
        if not request.session.get('user_id') or request.session.get('user_type') != 'customer':
            messages.warning(request, 'Please log in to view your dashboard.')
            return redirect('myapp:login')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer_id = self.request.session.get('user_id')
        
        # Get customer object
        customer = get_object_or_404(Customers, customer_id=customer_id)
        context['customer'] = customer
        
        # Get filter parameters
        selected_year = self.request.GET.get('year', '')
        selected_month = self.request.GET.get('month', '')
        
        # Base queryset - all orders for this customer
        orders_qs = Orders.objects.filter(customer=customer)
        
        # Get all years with orders
        years = orders_qs.dates('order_date', 'year', order='DESC')
        context['years'] = [year.year for year in years]
        context['selected_year'] = selected_year
        context['selected_month'] = selected_month
        
        # Filter by year if selected
        if selected_year:
            orders_qs = orders_qs.filter(order_date__year=int(selected_year))
            
            # Get months for selected year
            months = orders_qs.dates('order_date', 'month', order='ASC')
            context['months'] = [(month.month, calendar.month_name[month.month]) for month in months]
            
            # Filter by month if selected
            if selected_month:
                orders_qs = orders_qs.filter(order_date__month=int(selected_month))
        
        # Calculate summary statistics
        order_details = OrderDetails.objects.filter(order__in=orders_qs)
        
        summary = order_details.annotate(
            line_revenue=ExpressionWrapper(
                F('unit_price') * F('quantity') * (1 - F('discount')),
                output_field=FloatField()
            )
        ).aggregate(
            total_orders=Count('order', distinct=True),
            total_products=Sum('quantity'),
            total_revenue=Sum('line_revenue')
        )
        
        context['total_orders'] = summary['total_orders'] or 0
        context['total_products'] = summary['total_products'] or 0
        context['total_revenue'] = summary['total_revenue'] or 0
        context['avg_order_value'] = (summary['total_revenue'] / summary['total_orders']) if summary['total_orders'] else 0
        
        # Annual sales breakdown (for all years or selected year)
        if selected_year:
            # Monthly breakdown for selected year
            monthly_sales = order_details.annotate(
                month=TruncMonth('order__order_date'),
                line_revenue=ExpressionWrapper(
                    F('unit_price') * F('quantity') * (1 - F('discount')),
                    output_field=FloatField()
                )
            ).values('month').annotate(
                orders=Count('order', distinct=True),
                products=Sum('quantity'),
                revenue=Sum('line_revenue')
            ).order_by('month')
            context['monthly_sales'] = list(monthly_sales)
        else:
            # Yearly breakdown
            yearly_sales = order_details.annotate(
                year=TruncYear('order__order_date'),
                line_revenue=ExpressionWrapper(
                    F('unit_price') * F('quantity') * (1 - F('discount')),
                    output_field=FloatField()
                )
            ).values('year').annotate(
                orders=Count('order', distinct=True),
                products=Sum('quantity'),
                revenue=Sum('line_revenue')
            ).order_by('-year')
            context['yearly_sales'] = list(yearly_sales)
        
        # Top 10 products
        if selected_year:
            top_products_qs = order_details.filter(order__order_date__year=int(selected_year))
        else:
            top_products_qs = order_details
        
        top_products = top_products_qs.annotate(
            line_revenue=ExpressionWrapper(
                F('unit_price') * F('quantity') * (1 - F('discount')),
                output_field=FloatField()
            )
        ).values(
            'product__product_name',
            'product__product_id'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('line_revenue'),
            order_count=Count('order', distinct=True)
        ).order_by('-total_quantity')[:10]
        context['top_products'] = list(top_products)
        
        # Top 10 products by year (for year-over-year comparison)
        top_products_by_year = {}
        for year in context['years']:
            year_products = order_details.filter(
                order__order_date__year=year
            ).annotate(
                line_revenue=ExpressionWrapper(
                    F('unit_price') * F('quantity') * (1 - F('discount')),
                    output_field=FloatField()
                )
            ).values(
                'product__product_name',
                'product__product_id'
            ).annotate(
                total_quantity=Sum('quantity'),
                total_revenue=Sum('line_revenue')
            ).order_by('-total_quantity')[:10]
            top_products_by_year[year] = list(year_products)
        context['top_products_by_year'] = top_products_by_year
        
        # Top 10 categories
        top_categories = top_products_qs.annotate(
            line_revenue=ExpressionWrapper(
                F('unit_price') * F('quantity') * (1 - F('discount')),
                output_field=FloatField()
            )
        ).values(
            'product__category__category_name',
            'product__category__category_id'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('line_revenue'),
            order_count=Count('order', distinct=True)
        ).order_by('-total_quantity')[:10]
        context['top_categories'] = list(top_categories)
        
        # Top 10 categories by year (for year-over-year comparison)
        top_categories_by_year = {}
        for year in context['years']:
            year_categories = order_details.filter(
                order__order_date__year=year
            ).annotate(
                line_revenue=ExpressionWrapper(
                    F('unit_price') * F('quantity') * (1 - F('discount')),
                    output_field=FloatField()
                )
            ).values(
                'product__category__category_name',
                'product__category__category_id'
            ).annotate(
                total_quantity=Sum('quantity'),
                total_revenue=Sum('line_revenue')
            ).order_by('-total_quantity')[:10]
            top_categories_by_year[year] = list(year_categories)
        context['top_categories_by_year'] = top_categories_by_year
        
        # Recent orders
        recent_orders = orders_qs.order_by('-order_date')[:5]
        context['recent_orders'] = recent_orders
        
        # Product recommendations based on purchasing patterns
        recommended_products = get_product_recommendations(customer, limit=6)
        context['recommended_products'] = recommended_products
        
        return context


class ManagerDashboardView(TemplateView):
    """
    Manager/Employee dashboard for overall sales analytics
    Requirement 2: Product/Sales Analysis (45%)
    """
    template_name = 'myapp/manager_dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Check if employee/manager is logged in"""
        if not request.session.get('user_id') or request.session.get('user_type') != 'employee':
            messages.warning(request, 'Manager access required. Please log in.')
            return redirect('myapp:login')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee_id = self.request.session.get('user_id')
        
        # Get employee object
        employee = get_object_or_404(Employees, employee_id=employee_id)
        context['employee'] = employee
        
        # Get filter parameters
        selected_year = self.request.GET.get('year', '')
        selected_product = self.request.GET.get('product', '')
        
        # Base queryset - all orders
        orders_qs = Orders.objects.all()
        order_details_qs = OrderDetails.objects.all()
        
        # Get all years
        years = orders_qs.dates('order_date', 'year', order='DESC')
        context['years'] = [year.year for year in years]
        context['selected_year'] = selected_year
        context['selected_product'] = selected_product
        
        # Get all products that have been ordered
        products = Products.objects.filter(
            orderdetails__isnull=False
        ).distinct().order_by('product_name')
        context['products'] = products
        
        # Filter by year if selected
        if selected_year:
            orders_qs = orders_qs.filter(order_date__year=int(selected_year))
            order_details_qs = order_details_qs.filter(order__order_date__year=int(selected_year))
        
        # Overall statistics
        summary = order_details_qs.annotate(
            line_revenue=ExpressionWrapper(
                F('unit_price') * F('quantity') * (1 - F('discount')),
                output_field=FloatField()
            )
        ).aggregate(
            total_orders=Count('order', distinct=True),
            total_products=Sum('quantity'),
            total_revenue=Sum('line_revenue'),
            avg_discount=Avg('discount')
        )
        
        context['total_orders'] = summary['total_orders'] or 0
        context['total_products'] = summary['total_products'] or 0
        context['total_revenue'] = summary['total_revenue'] or 0
        context['avg_order_value'] = (summary['total_revenue'] / summary['total_orders']) if summary['total_orders'] else 0
        context['avg_discount'] = (summary['avg_discount'] * 100) if summary['avg_discount'] else 0
        
        # Yearly sales breakdown (Annual Sales Overview)
        yearly_sales = OrderDetails.objects.annotate(
            year=TruncYear('order__order_date'),
            line_revenue=ExpressionWrapper(
                F('unit_price') * F('quantity') * (1 - F('discount')),
                output_field=FloatField()
            )
        ).values('year').annotate(
            orders=Count('order', distinct=True),
            products=Sum('quantity'),
            revenue=Sum('line_revenue')
        ).order_by('-year')
        context['yearly_sales'] = list(yearly_sales)
        
        # Monthly sales breakdown (when year is selected or for all time)
        if selected_year:
            # Monthly breakdown for selected year
            monthly_sales = order_details_qs.annotate(
                month=TruncMonth('order__order_date'),
                line_revenue=ExpressionWrapper(
                    F('unit_price') * F('quantity') * (1 - F('discount')),
                    output_field=FloatField()
                )
            ).values('month').annotate(
                orders=Count('order', distinct=True),
                products=Sum('quantity'),
                revenue=Sum('line_revenue')
            ).order_by('month')
            context['monthly_sales'] = list(monthly_sales)
        else:
            # Monthly aggregate across all years
            monthly_sales_all = OrderDetails.objects.annotate(
                month_num=F('order__order_date__month'),
                line_revenue=ExpressionWrapper(
                    F('unit_price') * F('quantity') * (1 - F('discount')),
                    output_field=FloatField()
                )
            ).values('month_num').annotate(
                orders=Count('order', distinct=True),
                products=Sum('quantity'),
                revenue=Sum('line_revenue')
            ).order_by('month_num')
            context['monthly_sales_all'] = list(monthly_sales_all)
        
        # Top 10 revenue-generating products
        top_products = order_details_qs.annotate(
            line_revenue=ExpressionWrapper(
                F('unit_price') * F('quantity') * (1 - F('discount')),
                output_field=FloatField()
            )
        ).values(
            'product__product_name',
            'product__product_id',
            'product__category__category_name'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('line_revenue'),
            order_count=Count('order', distinct=True)
        ).order_by('-total_revenue')[:10]
        context['top_products'] = list(top_products)
        
        # Bottom 10 revenue-generating products (only products that have been sold)
        bottom_products = order_details_qs.annotate(
            line_revenue=ExpressionWrapper(
                F('unit_price') * F('quantity') * (1 - F('discount')),
                output_field=FloatField()
            )
        ).values(
            'product__product_name',
            'product__product_id',
            'product__category__category_name'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('line_revenue'),
            order_count=Count('order', distinct=True)
        ).order_by('total_revenue')[:10]
        context['bottom_products'] = list(bottom_products)
        
        # Category performance (Category Sales Analysis)
        category_performance = order_details_qs.annotate(
            line_revenue=ExpressionWrapper(
                F('unit_price') * F('quantity') * (1 - F('discount')),
                output_field=FloatField()
            )
        ).values(
            'product__category__category_name',
            'product__category__category_id'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('line_revenue'),
            order_count=Count('order', distinct=True),
            product_count=Count('product', distinct=True)
        ).order_by('-total_revenue')
        context['category_performance'] = list(category_performance)
        
        # PRODUCT SALES ANALYSIS - Individual Product Drill-Down
        if selected_product:
            product = get_object_or_404(Products, product_id=int(selected_product))
            context['product'] = product
            
            # Get order details for this specific product
            product_order_details_qs = OrderDetails.objects.filter(product=product)
            
            # Filter by year if selected
            if selected_year:
                product_order_details_qs = product_order_details_qs.filter(
                    order__order_date__year=int(selected_year)
                )
            
            # Product summary statistics
            product_summary = product_order_details_qs.annotate(
                line_revenue=ExpressionWrapper(
                    F('unit_price') * F('quantity') * (1 - F('discount')),
                    output_field=FloatField()
                )
            ).aggregate(
                total_orders=Count('order', distinct=True),
                total_quantity=Sum('quantity'),
                total_revenue=Sum('line_revenue'),
                avg_discount=Avg('discount'),
                avg_quantity_per_order=Avg('quantity')
            )
            context['product_summary'] = product_summary
            
            # Monthly breakdown for the selected product
            product_monthly_sales = product_order_details_qs.annotate(
                month=TruncMonth('order__order_date'),
                line_revenue=ExpressionWrapper(
                    F('unit_price') * F('quantity') * (1 - F('discount')),
                    output_field=FloatField()
                )
            ).values('month').annotate(
                orders=Count('order', distinct=True),
                quantity=Sum('quantity'),
                revenue=Sum('line_revenue')
            ).order_by('month')
            context['product_monthly_sales'] = list(product_monthly_sales)
            
            # Calculate average across all products for comparison
            all_products_stats = OrderDetails.objects.annotate(
                line_revenue=ExpressionWrapper(
                    F('unit_price') * F('quantity') * (1 - F('discount')),
                    output_field=FloatField()
                )
            ).aggregate(
                total_revenue=Sum('line_revenue'),
                total_count=Count('*'),
                avg_quantity=Avg('quantity')
            )
            
            # Calculate averages
            if all_products_stats['total_count'] and all_products_stats['total_count'] > 0:
                avg_revenue_per_line = all_products_stats['total_revenue'] / all_products_stats['total_count']
            else:
                avg_revenue_per_line = 0
            
            context['all_products_avg'] = {
                'avg_revenue_per_line': avg_revenue_per_line,
                'avg_quantity': all_products_stats['avg_quantity'] or 0
            }
        
        return context


class ProductAnalysisView(TemplateView):
    """
    Detailed product-level sales analysis
    Requirement 2: Product/Sales Analysis
    """
    template_name = 'myapp/product_analysis.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Check if employee/manager is logged in"""
        if not request.session.get('user_id') or request.session.get('user_type') != 'employee':
            messages.warning(request, 'Manager access required.')
            return redirect('myapp:login')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get filter parameters
        selected_product = self.request.GET.get('product', '')
        selected_year = self.request.GET.get('year', '')
        
        # Get all products that have been ordered
        products = Products.objects.filter(
            orderdetails__isnull=False
        ).distinct().order_by('product_name')
        context['products'] = products
        context['selected_product'] = selected_product
        context['selected_year'] = selected_year
        
        # Get all years for filter dropdown
        all_years = Orders.objects.dates('order_date', 'year', order='DESC')
        context['years'] = [year.year for year in all_years]
        
        # TOP 10 PRODUCTS ANALYSIS - Show always
        # All years
        top_products_all = OrderDetails.objects.annotate(
            line_revenue=ExpressionWrapper(
                F('unit_price') * F('quantity') * (1 - F('discount')),
                output_field=FloatField()
            )
        ).values(
            'product__product_name',
            'product__product_id'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('line_revenue')
        ).order_by('-total_quantity')[:10]
        top_products_all_list = list(top_products_all)
        context['top_products_all'] = top_products_all_list
        context['top_products_all_json'] = json.dumps(convert_to_json_safe(top_products_all_list))
        
        # By selected year (if year is selected)
        if selected_year:
            top_products_year = OrderDetails.objects.filter(
                order__order_date__year=int(selected_year)
            ).annotate(
                line_revenue=ExpressionWrapper(
                    F('unit_price') * F('quantity') * (1 - F('discount')),
                    output_field=FloatField()
                )
            ).values(
                'product__product_name',
                'product__product_id'
            ).annotate(
                total_quantity=Sum('quantity'),
                total_revenue=Sum('line_revenue')
            ).order_by('-total_quantity')[:10]
            top_products_year_list = list(top_products_year)
            context['top_products_year'] = top_products_year_list
            context['top_products_year_json'] = json.dumps(convert_to_json_safe(top_products_year_list))
        
        if selected_product:
            product = get_object_or_404(Products, product_id=int(selected_product))
            context['product'] = product
            
            # Get order details for this product
            order_details_qs = OrderDetails.objects.filter(product=product)
            
            # Get all years
            years = Orders.objects.filter(
                orderdetails__product=product
            ).dates('order_date', 'year', order='DESC')
            context['years'] = [year.year for year in years]
            
            # Filter by year if selected
            if selected_year:
                order_details_qs = order_details_qs.filter(order__order_date__year=int(selected_year))
            
            # Product summary statistics
            summary = order_details_qs.annotate(
                line_revenue=ExpressionWrapper(
                    F('unit_price') * F('quantity') * (1 - F('discount')),
                    output_field=FloatField()
                )
            ).aggregate(
                total_orders=Count('order', distinct=True),
                total_quantity=Sum('quantity'),
                total_revenue=Sum('line_revenue'),
                avg_discount=Avg('discount'),
                avg_quantity_per_order=Avg('quantity')
            )
            context['summary'] = summary
            
            # Monthly breakdown
            monthly_sales = order_details_qs.annotate(
                month=TruncMonth('order__order_date'),
                line_revenue=ExpressionWrapper(
                    F('unit_price') * F('quantity') * (1 - F('discount')),
                    output_field=FloatField()
                )
            ).values('month').annotate(
                orders=Count('order', distinct=True),
                quantity=Sum('quantity'),
                revenue=Sum('line_revenue')
            ).order_by('month')
            context['monthly_sales'] = list(monthly_sales)
            
            # Calculate average across all products for comparison
            all_products_stats = OrderDetails.objects.annotate(
                line_revenue=ExpressionWrapper(
                    F('unit_price') * F('quantity') * (1 - F('discount')),
                    output_field=FloatField()
                )
            ).aggregate(
                total_revenue=Sum('line_revenue'),
                total_count=Count('*')
            )
            # Calculate average manually
            if all_products_stats['total_count'] and all_products_stats['total_count'] > 0:
                avg_revenue = all_products_stats['total_revenue'] / all_products_stats['total_count']
            else:
                avg_revenue = 0
            
            context['all_products_avg'] = {'avg_revenue_per_product': avg_revenue}
        
        return context


class CategoryAnalysisView(TemplateView):
    """
    Category-level sales analysis
    Requirement 2: Product/Sales Analysis
    """
    template_name = 'myapp/category_analysis.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Check if employee/manager is logged in"""
        if not request.session.get('user_id') or request.session.get('user_type') != 'employee':
            messages.warning(request, 'Manager access required.')
            return redirect('myapp:login')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get filter parameters
        selected_category = self.request.GET.get('category', '')
        selected_year = self.request.GET.get('year', '')
        
        # Get all categories
        categories = Categories.objects.all().order_by('category_name')
        context['categories'] = categories
        context['selected_category'] = selected_category
        context['selected_year'] = selected_year
        
        # Get all years for filter dropdown
        all_years = Orders.objects.dates('order_date', 'year', order='DESC')
        context['years'] = [year.year for year in all_years]
        
        # TOP 10 CATEGORIES ANALYSIS - Show always
        # All years
        top_categories_all = OrderDetails.objects.annotate(
            line_revenue=ExpressionWrapper(
                F('unit_price') * F('quantity') * (1 - F('discount')),
                output_field=FloatField()
            )
        ).values(
            'product__category__category_name',
            'product__category__category_id'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('line_revenue')
        ).order_by('-total_quantity')[:10]
        top_categories_all_list = list(top_categories_all)
        context['top_categories_all'] = top_categories_all_list
        context['top_categories_all_json'] = json.dumps(convert_to_json_safe(top_categories_all_list))
        
        # By selected year (if year is selected)
        if selected_year:
            top_categories_year = OrderDetails.objects.filter(
                order__order_date__year=int(selected_year)
            ).annotate(
                line_revenue=ExpressionWrapper(
                    F('unit_price') * F('quantity') * (1 - F('discount')),
                    output_field=FloatField()
                )
            ).values(
                'product__category__category_name',
                'product__category__category_id'
            ).annotate(
                total_quantity=Sum('quantity'),
                total_revenue=Sum('line_revenue')
            ).order_by('-total_quantity')[:10]
            top_categories_year_list = list(top_categories_year)
            context['top_categories_year'] = top_categories_year_list
            context['top_categories_year_json'] = json.dumps(convert_to_json_safe(top_categories_year_list))
        
        if selected_category:
            category = get_object_or_404(Categories, category_id=int(selected_category))
            context['category'] = category
            
            # Get order details for products in this category
            order_details_qs = OrderDetails.objects.filter(product__category=category)
            
            # Get all years
            years = Orders.objects.filter(
                orderdetails__product__category=category
            ).dates('order_date', 'year', order='DESC')
            context['years'] = [year.year for year in years]
            
            # Filter by year if selected
            if selected_year:
                order_details_qs = order_details_qs.filter(order__order_date__year=int(selected_year))
            
            # Category summary statistics
            summary = order_details_qs.annotate(
                line_revenue=ExpressionWrapper(
                    F('unit_price') * F('quantity') * (1 - F('discount')),
                    output_field=FloatField()
                )
            ).aggregate(
                total_orders=Count('order', distinct=True),
                total_quantity=Sum('quantity'),
                total_revenue=Sum('line_revenue'),
                product_count=Count('product', distinct=True)
            )
            context['summary'] = summary
            
            # Monthly breakdown
            monthly_sales = order_details_qs.annotate(
                month=TruncMonth('order__order_date'),
                line_revenue=ExpressionWrapper(
                    F('unit_price') * F('quantity') * (1 - F('discount')),
                    output_field=FloatField()
                )
            ).values('month').annotate(
                orders=Count('order', distinct=True),
                quantity=Sum('quantity'),
                revenue=Sum('line_revenue')
            ).order_by('month')
            context['monthly_sales'] = list(monthly_sales)
            
            # Top products in this category
            top_products = order_details_qs.annotate(
                line_revenue=ExpressionWrapper(
                    F('unit_price') * F('quantity') * (1 - F('discount')),
                    output_field=FloatField()
                )
            ).values(
                'product__product_name',
                'product__product_id'
            ).annotate(
                total_quantity=Sum('quantity'),
                total_revenue=Sum('line_revenue'),
                order_count=Count('order', distinct=True)
            ).order_by('-total_revenue')[:10]
            context['top_products'] = list(top_products)
        
        return context
