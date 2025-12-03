# myapp/auth_backend.py
"""
Custom authentication backend for Customer model
Allows customers to login using their customer_id and password
"""
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from .models import Customers


class CustomerAuthBackend(BaseBackend):
    """
    Custom authentication backend for the Customers model.
    Authenticates using customer_id as username and password field.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate a customer using customer_id and password.
        
        Args:
            request: The HTTP request object
            username: The customer_id (e.g., 'ALFKI')
            password: The customer's password
            
        Returns:
            Customer object if authentication succeeds, None otherwise
        """
        try:
            # Look up customer by customer_id
            customer = Customers.objects.get(customer_id=username.upper())
            
            # Check if customer has a password set
            if not customer.password:
                return None
            
            # Check if customer is inactive
            if customer.inactive_date:
                return None
            
            # Verify password (stored as plain text for now - should be hashed in production)
            if customer.password == password:
                return customer
                
        except Customers.DoesNotExist:
            return None
        
        return None
    
    def get_user(self, user_id):
        """
        Get a customer by their customer_id.
        Required by Django's authentication system.
        
        Args:
            user_id: The customer_id
            
        Returns:
            Customer object or None
        """
        try:
            return Customers.objects.get(pk=user_id)
        except Customers.DoesNotExist:
            return None


class EmployeeAuthBackend(BaseBackend):
    """
    Custom authentication backend for the Employees model.
    Allows managers/employees to login using employee_id and a password.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate an employee using employee_id.
        For now, we'll use a simple check - enhance with password field later.
        
        Args:
            request: The HTTP request object
            username: The employee_id (as string)
            password: The employee's password
            
        Returns:
            Employee object if authentication succeeds, None otherwise
        """
        from .models import Employees
        
        try:
            # Look up employee by employee_id
            employee_id = int(username)
            employee = Employees.objects.get(employee_id=employee_id)
            
            # For now, use a simple password check
            # In production, add a password field to Employees model
            # Temporary: accept any employee_id with password "manager123"
            if password == "manager123":
                return employee
                
        except (ValueError, Employees.DoesNotExist):
            return None
        
        return None
    
    def get_user(self, user_id):
        """
        Get an employee by their employee_id.
        
        Args:
            user_id: The employee_id
            
        Returns:
            Employee object or None
        """
        from .models import Employees
        
        try:
            return Employees.objects.get(pk=user_id)
        except Employees.DoesNotExist:
            return None
