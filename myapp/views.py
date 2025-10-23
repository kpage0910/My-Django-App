# views.py 
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from datetime import datetime, date, timedelta
from decimal import Decimal

from .models import (
    Customers, Products, Categories, Orders, OrderDetails, 
    Suppliers, Employees, Shippers
)
from .forms import CustomerForm, OrderForm, ProductForm
from .cart_utils import (
    get_cart, add_to_cart, remove_from_cart, 
    clear_cart, get_cart_items, validate_cart
)

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

class CustomerListView(ListView):
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
        
        # Add customer's orders to context, sorted by most recent first
        context['orders'] = Orders.objects.filter(
            customer=self.object
        ).select_related('ship_via', 'employee').order_by('-order_date')
        
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
        messages.success(self.request, f'Customer "{form.instance.company_name}" has been created successfully!')
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

class ProductListView(ListView):
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
                
                # Create order details from cart items
                for item in cart_data['items']:
                    OrderDetails.objects.create(
                        order=self.object,
                        product=item['product'],
                        unit_price=item['product'].unit_price,
                        quantity=item['quantity'],
                        discount=0.00  # Default discount
                    )
                
                # Clear the cart after successful order
                clear_cart(self.request)
                
                messages.success(
                    self.request,
                    f'Order #{self.object.order_id} created successfully for {customer.company_name}!'
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