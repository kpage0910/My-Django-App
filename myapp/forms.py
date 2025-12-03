from django import forms
from django.core.validators import RegexValidator
from .models import Customers, Orders, OrderDetails, Employees, Shippers, Products, Categories, Suppliers
from datetime import date, timedelta
import re

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customers
        fields = [
            'company_name', 'contact_name', 'contact_title',
            'address', 'city', 'region', 'postal_code', 'country', 
            'phone', 'fax', 'password'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_title': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'region': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'fax': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def clean_company_name(self):
        company_name = self.cleaned_data.get('company_name')
        if company_name:
            # Remove extra whitespace
            company_name = ' '.join(company_name.split())
            
            # Check if empty after stripping
            if not company_name.strip():
                raise forms.ValidationError("Company name cannot be empty or only whitespace.")
            
            # Check if company name contains only numbers
            if company_name.isdigit():
                raise forms.ValidationError("Company name cannot contain only numbers.")
            
            # Check minimum length
            if len(company_name) < 2:
                raise forms.ValidationError("Company name must be at least 2 characters long.")
            
            # Check for duplicate company names (case-insensitive)
            duplicate_check = Customers.objects.filter(company_name__iexact=company_name)
            if self.instance.pk:
                duplicate_check = duplicate_check.exclude(customer_id=self.instance.pk)
            
            if duplicate_check.exists():
                raise forms.ValidationError(f"A customer with the company name '{company_name}' already exists.")
        else:
            raise forms.ValidationError("Company name is required.")
        
        return company_name

    def clean_contact_name(self):
        contact_name = self.cleaned_data.get('contact_name')
        if contact_name:
            # Remove extra whitespace
            contact_name = ' '.join(contact_name.split())
            
            # Check if contains numbers
            if any(char.isdigit() for char in contact_name):
                raise forms.ValidationError("Contact name should not contain numbers.")
            
            # Check for valid characters (letters, spaces, hyphens, periods, apostrophes)
            if not re.match(r'^[a-zA-Z\s\-\.\']+$', contact_name):
                raise forms.ValidationError("Contact name contains invalid characters. Only letters, spaces, hyphens, periods, and apostrophes are allowed.")
            
            # Check minimum length if provided
            if len(contact_name) < 2:
                raise forms.ValidationError("Contact name must be at least 2 characters long.")
        
        return contact_name

    def clean_city(self):
        city = self.cleaned_data.get('city')
        if city:
            # Remove extra whitespace
            city = ' '.join(city.split())
            
            # Check if contains numbers
            if any(char.isdigit() for char in city):
                raise forms.ValidationError("City name should not contain numbers.")
            
            # Check for valid characters
            if not re.match(r'^[a-zA-Z\s\-\.\']+$', city):
                raise forms.ValidationError("City name contains invalid characters.")
            
            # Check minimum length
            if len(city) < 2:
                raise forms.ValidationError("City name must be at least 2 characters long.")
        
        return city

    def clean_country(self):
        country = self.cleaned_data.get('country')
        if country:
            # Remove extra whitespace
            country = ' '.join(country.split())
            
            # Check if contains numbers
            if any(char.isdigit() for char in country):
                raise forms.ValidationError("Country name should not contain numbers.")
            
            # Check for valid characters
            if not re.match(r'^[a-zA-Z\s\-\.\']+$', country):
                raise forms.ValidationError("Country name contains invalid characters.")
            
            # Check minimum length
            if len(country) < 2:
                raise forms.ValidationError("Country name must be at least 2 characters long.")
        
        return country

    def clean_postal_code(self):
        postal_code = self.cleaned_data.get('postal_code')
        if postal_code:
            # Remove extra whitespace
            postal_code = postal_code.strip()
            
            # Check for valid characters (alphanumeric, spaces, hyphens)
            if not re.match(r'^[a-zA-Z0-9\s\-]+$', postal_code):
                raise forms.ValidationError("Postal code contains invalid characters. Only letters, numbers, spaces, and hyphens are allowed.")
            
            # Check minimum length
            if len(postal_code) < 3:
                raise forms.ValidationError("Postal code must be at least 3 characters long.")
        
        return postal_code

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove extra whitespace
            phone = phone.strip()
            
            # Check for valid characters (digits, +, -, (, ), spaces, .)
            if not re.match(r'^[\d\+\-\(\)\s\.]+$', phone):
                raise forms.ValidationError("Phone number contains invalid characters. Only digits, +, -, (, ), spaces, and periods are allowed.")
            
            # Check minimum length (at least 7 digits for a valid phone number)
            digits_only = re.sub(r'[^\d]', '', phone)
            if len(digits_only) < 7:
                raise forms.ValidationError("Phone number must contain at least 7 digits.")
        
        return phone

    def clean_fax(self):
        fax = self.cleaned_data.get('fax')
        if fax:
            # Remove extra whitespace
            fax = fax.strip()
            
            # Check for valid characters
            if not re.match(r'^[\d\+\-\(\)\s\.]+$', fax):
                raise forms.ValidationError("Fax number contains invalid characters. Only digits, +, -, (, ), spaces, and periods are allowed.")
            
            # Check minimum length
            digits_only = re.sub(r'[^\d]', '', fax)
            if len(digits_only) < 7:
                raise forms.ValidationError("Fax number must contain at least 7 digits.")
        
        return fax

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            # Check minimum length
            if len(password) < 6:
                raise forms.ValidationError("Password must be at least 6 characters long.")
            
            # Check maximum length
            if len(password) > 64:
                raise forms.ValidationError("Password cannot exceed 64 characters.")
        
        return password


# ======================== ORDER FORMS ========================

class OrderForm(forms.ModelForm):
    """
    Form for creating orders with shipping and employee information
    """
    class Meta:
        model = Orders
        fields = [
            'employee', 'order_date', 'required_date', 'ship_via',
            'ship_name', 'ship_address', 'ship_city', 'ship_region',
            'ship_postal_code', 'ship_country', 'freight'
        ]
        widgets = {
            'employee': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'order_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'readonly': True
            }),
            'required_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'ship_via': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'ship_name': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'ship_address': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'ship_city': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'ship_region': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'ship_postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'ship_country': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'freight': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            })
        }
        labels = {
            'employee': 'Assigned Employee *',
            'order_date': 'Order Date',
            'required_date': 'Required Delivery Date *',
            'ship_via': 'Shipping Method *',
            'ship_name': 'Ship To Name',
            'ship_address': 'Shipping Address',
            'ship_city': 'City',
            'ship_region': 'State/Region',
            'ship_postal_code': 'Postal Code',
            'ship_country': 'Country',
            'freight': 'Freight Cost'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set default values
        if not self.instance.pk:  # New order
            self.initial['order_date'] = date.today()
            self.initial['required_date'] = date.today() + timedelta(days=21)
            self.initial['freight'] = 0.00
        
        # Populate employee choices
        self.fields['employee'].queryset = Employees.objects.all().order_by('last_name', 'first_name')
        self.fields['employee'].empty_label = "-- Select an Employee --"
        
        # Populate shipper choices
        self.fields['ship_via'].queryset = Shippers.objects.all().order_by('company_name')
        self.fields['ship_via'].empty_label = "-- Select Shipping Method --"
    
    def clean_required_date(self):
        required_date = self.cleaned_data.get('required_date')
        order_date = self.cleaned_data.get('order_date') or date.today()
        
        if required_date and required_date < order_date:
            raise forms.ValidationError("Required date cannot be before order date.")
        
        return required_date
    
# ======================== PRODUCT FORMS ========================

class ProductForm(forms.ModelForm):
    """
    Form for creating and editing products with comprehensive validation
    """
    class Meta:
        model = Products
        fields = [
            'product_name', 'supplier', 'category', 'quantity_per_unit',
            'unit_price', 'units_in_stock', 'units_on_order', 
            'reorder_level', 'discontinued'
        ]
        widgets = {
            'product_name': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'maxlength': '40'
            }),
            'supplier': forms.Select(attrs={
                'class': 'form-select'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'quantity_per_unit': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '20',
                'placeholder': 'e.g., 10 boxes x 20 bags'
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'units_in_stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'units_on_order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'reorder_level': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'discontinued': forms.Select(
                choices=[(0, 'Active'), (1, 'Discontinued')],
                attrs={'class': 'form-select'}
            )
        }
        labels = {
            'product_name': 'Product Name *',
            'supplier': 'Supplier',
            'category': 'Category',
            'quantity_per_unit': 'Quantity Per Unit',
            'unit_price': 'Unit Price ($)',
            'units_in_stock': 'Units in Stock',
            'units_on_order': 'Units on Order',
            'reorder_level': 'Reorder Level',
            'discontinued': 'Status'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set default values for new products
        if not self.instance.pk:
            self.initial['discontinued'] = 0
            self.initial['units_in_stock'] = 0
            self.initial['units_on_order'] = 0
            self.initial['reorder_level'] = 0
            self.initial['unit_price'] = 0.00
        
        # Populate category choices
        self.fields['category'].queryset = Categories.objects.all().order_by('category_name')
        self.fields['category'].empty_label = "-- Select a Category --"
        
        # Populate supplier choices
        self.fields['supplier'].queryset = Suppliers.objects.all().order_by('company_name')
        self.fields['supplier'].empty_label = "-- Select a Supplier --"
    
    def clean_product_name(self):
        """Validate product name"""
        product_name = self.cleaned_data.get('product_name')
        
        if product_name:
            # Remove extra whitespace
            product_name = ' '.join(product_name.split())
            
            # Check if not empty after stripping
            if not product_name.strip():
                raise forms.ValidationError("Product name cannot be empty or only whitespace.")
            
            # Check if product name contains only numbers
            if product_name.isdigit():
                raise forms.ValidationError("Product name cannot contain only numbers.")
            
            # Check minimum length
            if len(product_name) < 2:
                raise forms.ValidationError("Product name must be at least 2 characters long.")
            
            # Check for duplicate product names (case-insensitive)
            # Allow same name for the product being edited
            duplicate_check = Products.objects.filter(product_name__iexact=product_name)
            if self.instance.pk:
                duplicate_check = duplicate_check.exclude(product_id=self.instance.pk)
            
            if duplicate_check.exists():
                raise forms.ValidationError(f"A product with the name '{product_name}' already exists.")
        
        return product_name
    
    def clean_unit_price(self):
        """Validate unit price"""
        unit_price = self.cleaned_data.get('unit_price')
        
        if unit_price is not None:
            if unit_price < 0:
                raise forms.ValidationError("Unit price cannot be negative.")
            
            if unit_price > 999999.99:
                raise forms.ValidationError("Unit price cannot exceed $999,999.99.")
        
        return unit_price
    
    def clean_units_in_stock(self):
        """Validate units in stock"""
        units_in_stock = self.cleaned_data.get('units_in_stock')
        
        if units_in_stock is not None:
            if units_in_stock < 0:
                raise forms.ValidationError("Units in stock cannot be negative.")
            
            if units_in_stock > 32767:
                raise forms.ValidationError("Units in stock cannot exceed 32,767.")
        
        return units_in_stock
    
    def clean_units_on_order(self):
        """Validate units on order"""
        units_on_order = self.cleaned_data.get('units_on_order')
        
        if units_on_order is not None:
            if units_on_order < 0:
                raise forms.ValidationError("Units on order cannot be negative.")
            
            if units_on_order > 32767:
                raise forms.ValidationError("Units on order cannot exceed 32,767.")
        
        return units_on_order
    
    def clean_reorder_level(self):
        """Validate reorder level"""
        reorder_level = self.cleaned_data.get('reorder_level')
        
        if reorder_level is not None:
            if reorder_level < 0:
                raise forms.ValidationError("Reorder level cannot be negative.")
            
            if reorder_level > 32767:
                raise forms.ValidationError("Reorder level cannot exceed 32,767.")
        
        return reorder_level
    
    def clean_quantity_per_unit(self):
        """Validate quantity per unit"""
        quantity_per_unit = self.cleaned_data.get('quantity_per_unit')
        
        if quantity_per_unit:
            # Remove extra whitespace
            quantity_per_unit = ' '.join(quantity_per_unit.split())
            
            # Check minimum length
            if len(quantity_per_unit) < 2:
                raise forms.ValidationError("Quantity per unit must be at least 2 characters long.")
        
        return quantity_per_unit
    
    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()
        
        units_in_stock = cleaned_data.get('units_in_stock')
        units_on_order = cleaned_data.get('units_on_order')
        reorder_level = cleaned_data.get('reorder_level')
        discontinued = cleaned_data.get('discontinued')
        unit_price = cleaned_data.get('unit_price')
        
        # Check if unit price is set when product is active
        if discontinued == 0 and (unit_price is None or unit_price <= 0):
            self.add_error('unit_price', forms.ValidationError(
                "Active products must have a unit price greater than $0.00."
            ))
        
        # Warning if stock is below reorder level
        if units_in_stock is not None and reorder_level is not None:
            if units_in_stock < reorder_level and discontinued == 0:
                # This is just a warning, not an error
                self.add_error(None, forms.ValidationError(
                    f"Warning: Stock level ({units_in_stock}) is below reorder level ({reorder_level}).",
                    code='low_stock_warning'
                ))
        
        # Warning if discontinuing a product with stock on order
        if discontinued == 1 and units_on_order is not None and units_on_order > 0:
            self.add_error(None, forms.ValidationError(
                f"Warning: You are discontinuing a product with {units_on_order} units on order.",
                code='discontinued_with_orders_warning'
            ))
        
        return cleaned_data