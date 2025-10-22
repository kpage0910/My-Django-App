from django import forms
from django.core.validators import RegexValidator
from .models import Customers, Orders, OrderDetails, Employees, Shippers, Products
from datetime import date, timedelta
import re

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customers
        fields = [
            'customer_id', 'company_name', 'contact_name', 'contact_title',
            'address', 'city', 'region', 'postal_code', 'country', 
            'phone', 'fax', 'password'
        ]
        widgets = {
            'customer_id': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '5'}),
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

    def clean_customer_id(self):
        customer_id = self.cleaned_data.get('customer_id')
        if customer_id:
            if len(customer_id) != 5:
                raise forms.ValidationError("Customer ID must be exactly 5 characters long.")
            if not customer_id.isalnum():
                raise forms.ValidationError("Customer ID must contain only letters and numbers.")
            
            if not self.instance.pk and Customers.objects.filter(customer_id=customer_id).exists():
                raise forms.ValidationError("A customer with this ID already exists.")
        return customer_id.upper() if customer_id else customer_id

    def clean_company_name(self):
        company_name = self.cleaned_data.get('company_name')
        if company_name:
            if company_name.isdigit():
                raise forms.ValidationError("Company name cannot contain only numbers.")
            company_name = ' '.join(company_name.split())
        return company_name

    def clean_contact_name(self):
        contact_name = self.cleaned_data.get('contact_name')
        if contact_name:
            if any(char.isdigit() for char in contact_name):
                raise forms.ValidationError("Contact name should not contain numbers.")
            if not re.match(r'^[a-zA-Z\s\-\.\']+$', contact_name):
                raise forms.ValidationError("Contact name contains invalid characters.")
            contact_name = ' '.join(contact_name.split())
        return contact_name

    def clean_postal_code(self):
        postal_code = self.cleaned_data.get('postal_code')
        if postal_code:
            if not re.match(r'^[a-zA-Z0-9\s\-]+$', postal_code):
                raise forms.ValidationError("Postal code contains invalid characters.")
        return postal_code

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            if not re.match(r'^[\d\+\-\(\)\s\.]+$', phone):
                raise forms.ValidationError("Phone number contains invalid characters.")
        return phone

    def clean_fax(self):
        fax = self.cleaned_data.get('fax')
        if fax:
            if not re.match(r'^[\d\+\-\(\)\s\.]+$', fax):
                raise forms.ValidationError("Fax number contains invalid characters.")
        return fax


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