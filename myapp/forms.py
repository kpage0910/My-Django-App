from django import forms
from django.core.validators import RegexValidator
from .models import Customers
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
            # Customer ID should be exactly 5 characters, alphanumeric
            if len(customer_id) != 5:
                raise forms.ValidationError("Customer ID must be exactly 5 characters long.")
            if not customer_id.isalnum():
                raise forms.ValidationError("Customer ID must contain only letters and numbers.")
            
            # Check if customer_id already exists (only for new customers)
            if not self.instance.pk and Customers.objects.filter(customer_id=customer_id).exists():
                raise forms.ValidationError("A customer with this ID already exists.")
        return customer_id.upper() if customer_id else customer_id

    def clean_company_name(self):
        company_name = self.cleaned_data.get('company_name')
        if company_name:
            # Company name should not contain only numbers
            if company_name.isdigit():
                raise forms.ValidationError("Company name cannot contain only numbers.")
            # Remove extra whitespace
            company_name = ' '.join(company_name.split())
        return company_name

    def clean_contact_name(self):
        contact_name = self.cleaned_data.get('contact_name')
        if contact_name:
            # Names should not have numbers
            if any(char.isdigit() for char in contact_name):
                raise forms.ValidationError("Contact name should not contain numbers.")
            # Check for reasonable name format
            if not re.match(r'^[a-zA-Z\s\-\.\']+$', contact_name):
                raise forms.ValidationError("Contact name contains invalid characters.")
            contact_name = ' '.join(contact_name.split())
        return contact_name

    def clean_postal_code(self):
        postal_code = self.cleaned_data.get('postal_code')
        if postal_code:
            # Basic postal code validation - alphanumeric with optional spaces/hyphens
            if not re.match(r'^[a-zA-Z0-9\s\-]+$', postal_code):
                raise forms.ValidationError("Postal code contains invalid characters.")
        return postal_code

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove common phone number formatting
            cleaned_phone = re.sub(r'[\s\-\(\)\.]+', '', phone)
            # Check if remaining characters are digits or common phone symbols
            if not re.match(r'^[\d\+\-\(\)\s\.]+$', phone):
                raise forms.ValidationError("Phone number contains invalid characters.")
        return phone

    def clean_fax(self):
        fax = self.cleaned_data.get('fax')
        if fax:
            # Same validation as phone
            if not re.match(r'^[\d\+\-\(\)\s\.]+$', fax):
                raise forms.ValidationError("Fax number contains invalid characters.")
        return fax