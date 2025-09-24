# Import Django functionality we need
from lib2to3.fixes.fix_input import context
from django.shortcuts import render  # For rendering templates with context data
from django.db import connection
from django.views.generic import ListView, DetailView  # Pre-built Django view classes
from django.db.models import Q  # For complex database queries with OR conditions
from datetime import datetime  # Python's date/time functionality
from .models import Customers, Products, Categories, Orders, OrderDetails, Suppliers  # Import our Customer model from models.py

def home(request):
    """
    Function-based view for the home page
    
    Args:
        request: HTTP request object containing all request information
        
    Returns:
        HttpResponse: Rendered HTML page with context data
    """
    # Get current date and format it as "Monday December 09, 2024"
    timeNow = datetime.today().strftime("%A %B %d, %Y")
    
    # Render the home template with context data
    return render(
        request=request,  # Pass the request object
        template_name="myapp/home.html",  # Which template file to use
        context={  # Dictionary of data to send to template
            "today": timeNow,  # Current date for {{ today }} in template
            "title": "Django Traders 1.0"  # Page title for {{ title }} in template
        },
    )

class CustomerListView(ListView):
    """
    Class-based view for displaying a list of customers with search and sort functionality
    
    ListView is a Django built-in class that automatically handles:
    - Fetching objects from database
    - Pagination
    - Template rendering
    - Context variable creation
    """
    
    # Tell Django which model to work with
    model = Customers
    
    # Specify which template to use for rendering
    template_name = 'myapp/customer_list.html'
    
    # Name for the object list in template (default would be 'object_list')
    context_object_name = 'customers'
    
    # Enable pagination - show 25 customers per page
    paginate_by = 25
    
    def get_queryset(self):
        """
        Override the default queryset to add search and filtering functionality
        
        This method runs before the template is rendered and determines
        which customers to display based on user input
        
        Returns:
            QuerySet: Filtered and sorted customer records
        """
        # Start with all customers from the database
        queryset = Customers.objects.all()
        
        # Get search parameters from the URL query string
        # Example URL: /customers/?contact=John&city=London&sort=company_name
        contact_filter = self.request.GET.get('contact', '')  # Get 'contact' parameter or empty string
        contact_title_filter = self.request.GET.get('contact_title', '')  # Get 'contact_title' or empty
        contact_address_filter = self.request.GET.get('`address', '')  # Get 'address' or empty
        city_filter = self.request.GET.get('city', '')  # Get 'city' parameter or empty string
        country_filter = self.request.GET.get('country', '')  # Get 'country' parameter or empty string
        region_filter = self.request.GET.get('region', '')  # Get 'region' parameter or empty string
        
        # Apply filters if user provided search terms
        # icontains = case-insensitive search that matches partial text
        if contact_filter:
            # Filter customers where contact_name contains the search term
            queryset = queryset.filter(contact_name__icontains=contact_filter)
            
        if contact_title_filter:
            # Filter customers where contact_title contains the search term
            queryset = queryset.filter(contact_title__icontains=contact_title_filter)

        if contact_address_filter:
            # Filter customers where contact_address contains the search term
            queryset = queryset.filter(contact_address__icontains=contact_address_filter)
            
        if city_filter:
            # Filter customers where city contains the search term
            queryset = queryset.filter(city__icontains=city_filter)
            
        if country_filter:
            # Filter customers where country contains the search term
            queryset = queryset.filter(country__icontains=country_filter)
            
        if region_filter:
            # Filter customers where region contains the search term
            queryset = queryset.filter(region__icontains=region_filter)
        
        # Handle sorting by column
        # Example: ?sort=company_name or ?sort=-company_name (descending)
        sort_by = self.request.GET.get('sort', 'company_name')  # Default sort by company name
        if sort_by:
            # Apply sorting to the queryset
            queryset = queryset.order_by(sort_by)
            
        # Return the final filtered and sorted queryset
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        Add extra context data to send to the template
        
        This method runs after get_queryset() and adds additional
        variables that the template can use
        
        Args:
            **kwargs: Default context data from ListView
            
        Returns:
            dict: Complete context dictionary for template
        """
        # Get the default context data from ListView parent class
        # This includes 'customers', 'is_paginated', 'page_obj', etc.
        context = super().get_context_data(**kwargs)
        
        # Add search parameters to context so template can remember form values
        # This ensures search fields stay filled out after user searches
        context['contact_filter'] = self.request.GET.get('contact', '')
        context['contact_title_filter'] = self.request.GET.get('contact_title', '')
        context['address_filter'] = self.request.GET.get('address', '') 
        context['city_filter'] = self.request.GET.get('city', '')
        context['country_filter'] = self.request.GET.get('country', '')
        context['region_filter'] = self.request.GET.get('region', '')
        
        # Add current sort field to context for template to highlight active sort
        context['current_sort'] = self.request.GET.get('sort', 'company_name')
        
        # Add page title for template
        context['title'] = 'Customer Management - Django Traders'

         # Calculate starting number for pagination
        if context['is_paginated']:
            page_obj = context['page_obj']
            context['start_index'] = (page_obj.number - 1) * self.paginate_by
        else:
            context['start_index'] = 0
        # Return complete context dictionary to template
        return context

class CustomerDetailView(DetailView):
    """
    Class-based view for displaying individual customer details
    
    DetailView automatically:
    - Gets one customer based on URL parameter (pk)
    - Passes it to template as 'customer' (or 'object')
    - Handles 404 if customer doesn't exist
    """
    
    # Tell Django which model to work with
    model = Customers
    
    # Specify which template to use
    template_name = 'myapp/customer_detail.html'
    
    # Name for the customer object in template
    context_object_name = 'customer'
    
    def get_context_data(self, **kwargs):
        """
        Add extra context data for the customer detail template
        
        Args:
            **kwargs: Default context data from DetailView
            
        Returns:
            dict: Complete context dictionary for template
        """
        # Get default context from DetailView parent class
        # This includes 'customer' object
        context = super().get_context_data(**kwargs)
        
        # Add page title using the customer's company name
        # self.object contains the customer Django automatically found
        context['title'] = f'Customer Details: {self.object.company_name}'

        # Add customer's orders to context
        context['orders'] = Orders.objects.filter(customer=self.object)
        
        # Return context to template
        return context
    
class ProductListView(ListView):
    """
    Class-based view for displaying a list of products with search and sort functionality
    
    Similar to CustomerListView but for products
    """
    
    # Tell Django which model to work with
    model = Products
    
    # Specify which template to use for rendering
    template_name = 'myapp/product_list.html'
    
    # Name for the object list in template
    context_object_name = 'products'
    
    # Enable pagination - show 25 products per page
    paginate_by = 25
    
    def get_queryset(self):
        """
        Override the default queryset to add search and filtering functionality
        for products
        
        Returns:
            QuerySet: Filtered and sorted product records
        """
        # Start with all products and include related category data to avoid extra queries
        queryset = Products.objects.select_related('category').all()
        
        # Get search parameters from the URL query string
        product_name_filter = self.request.GET.get('product_name', '')
        category_filter = self.request.GET.get('category', '')
        supplier_filter = self.request.GET.get('supplier', '')
        discontinued_filter = self.request.GET.get('discontinued', '')
        
        # Apply filters if user provided search terms
        if product_name_filter:
            queryset = queryset.filter(product_name__icontains=product_name_filter)
            
        if category_filter:
            # Search by category name 
            queryset = queryset.filter(category_id=category_filter)

        if supplier_filter:
            queryset = queryset.filter(supplier_id=supplier_filter)
            
        if discontinued_filter:
            # Filter by discontinued status
            if discontinued_filter.lower() in ['true', '1', 'yes', 'discontinued']:
                queryset = queryset.filter(discontinued=1)
            elif discontinued_filter.lower() in ['false', '0', 'no', 'active']:
                queryset = queryset.filter(discontinued=0)
        
        # Handle sorting by column
        sort_by = self.request.GET.get('sort', 'product_name')  # Default sort by product name
        if sort_by:
            # Handle special case for category sorting
            if sort_by == 'category':
                sort_by = 'category__category_name'
            elif sort_by == '-category':
                sort_by = '-category__category_name'
            
            queryset = queryset.order_by(sort_by)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        Add extra context data to send to the template
        
        Returns:
            dict: Complete context dictionary for template
        """
        context = super().get_context_data(**kwargs)
        
        # Add search parameters to context so template can remember form values
        context['product_name_filter'] = self.request.GET.get('product_name', '')
        context['category_filter'] = self.request.GET.get('category', '')
        context['supplier_filter'] = self.request.GET.get('supplier', '')
        context['discontinued_filter'] = self.request.GET.get('discontinued', '')
        
        # Add current sort field to context
        context['current_sort'] = self.request.GET.get('sort', 'product_name')
        
        # Add page title for template
        context['title'] = 'Product Management - Django Traders'

        # Add filter options for categories and suppliers
        context['categories'] = Categories.objects.all().order_by('category_name')
        context['suppliers'] = Suppliers.objects.all().order_by('company_name')

        # Calculate starting number for pagination
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
    
    # Tell Django which model to work with
    model = Products
    
    # Specify which template to use
    template_name = 'myapp/product_detail.html'
    
    # Name for the product object in template
    context_object_name = 'product'
    
    def get_queryset(self):
        """
        Override to include related category data
        """
        return Products.objects.select_related('category')
    
    def get_context_data(self, **kwargs):
        """
        Add extra context data for the product detail template
        """
        context = super().get_context_data(**kwargs)
        
        # Add page title using the product's name
        context['title'] = f'Product Details: {self.object.product_name}'
        
        return context
    
class OrderDetailView(DetailView):
    """
    OrderDetailView using raw SQL to bypass Django ORM composite key limitations
    """
    
    model = Orders
    template_name = 'myapp/order_detail.html'
    context_object_name = 'order'
    
    def get_queryset(self):
        return Orders.objects.select_related('customer')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Order Details: #{self.object.order_id}'
        
        # Use raw SQL to get order details and avoid Django ORM primary key issues
        order_details = []
        subtotal = 0
        total_items = 0
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    od.order_id,
                    od.product_id,
                    od.unit_price,
                    od.quantity,
                    od.discount,
                    p.product_name,
                    p.discontinued,
                    c.category_name
                FROM order_details od
                JOIN products p ON od.product_id = p.product_id
                LEFT JOIN categories c ON p.category_id = c.category_id
                WHERE od.order_id = %s
                ORDER BY p.product_name
            """, [self.object.order_id])
            
            for row in cursor.fetchall():
                order_id, product_id, unit_price, quantity, discount, product_name, discontinued, category_name = row
                
                # Create a simple data object to hold the order detail information
                class OrderDetailData:
                    def __init__(self):
                        self.product_id = product_id
                        self.unit_price = unit_price
                        self.quantity = quantity
                        self.discount = discount
                        self.product_name = product_name
                        self.is_discontinued = discontinued == 1
                        self.category_name = category_name or "N/A"
                        self.line_total = unit_price * quantity * (1 - discount)
                        self.discount_percentage = int(discount * 100) if discount > 0 else 0
                
                detail = OrderDetailData()
                order_details.append(detail)
                subtotal += detail.line_total
                total_items += quantity
        
        context['order_details'] = order_details
        context['subtotal'] = subtotal
        context['total_items'] = total_items
        context['total'] = subtotal + (self.object.freight or 0)
        
        return context