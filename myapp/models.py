# myapp/models.py
from django.db import models

class Categories(models.Model):
    category_id = models.SmallIntegerField(primary_key=True)
    category_name = models.CharField(max_length=15)
    description = models.TextField(blank=True, null=True)
    picture = models.BinaryField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'categories'
    
    def __str__(self):
        return self.category_name

class CustomerDemographics(models.Model):
    customer_type_id = models.CharField(primary_key=True, max_length=5)
    customer_desc = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'customer_demographics'

    def __str__(self):
        return self.customer_type_id

class Customers(models.Model):
    customer_id = models.CharField(primary_key=True, max_length=5)
    company_name = models.CharField(max_length=40)
    contact_name = models.CharField(max_length=30, blank=True, null=True)
    contact_title = models.CharField(max_length=30, blank=True, null=True)
    address = models.CharField(max_length=60, blank=True, null=True)
    city = models.CharField(max_length=15, blank=True, null=True)
    region = models.CharField(max_length=15, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    country = models.CharField(max_length=15, blank=True, null=True)
    phone = models.CharField(max_length=24, blank=True, null=True)
    fax = models.CharField(max_length=24, blank=True, null=True)
    password = models.CharField(db_column='Password', max_length=64, blank=True, null=True)
    inactive_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'customers'

    def __str__(self):
        return f"{self.company_name} ({self.customer_id})"

class CustomerCustomerDemo(models.Model):
    customer = models.ForeignKey(Customers, models.DO_NOTHING, primary_key=True)
    customer_type = models.ForeignKey(CustomerDemographics, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'customer_customer_demo'
        unique_together = (('customer', 'customer_type'),)

class Suppliers(models.Model):
    supplier_id = models.SmallIntegerField(primary_key=True)
    company_name = models.CharField(max_length=40)
    contact_name = models.CharField(max_length=30, blank=True, null=True)
    contact_title = models.CharField(max_length=30, blank=True, null=True)
    address = models.CharField(max_length=60, blank=True, null=True)
    city = models.CharField(max_length=15, blank=True, null=True)
    region = models.CharField(max_length=15, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    country = models.CharField(max_length=15, blank=True, null=True)
    phone = models.CharField(max_length=24, blank=True, null=True)
    fax = models.CharField(max_length=24, blank=True, null=True)
    homepage = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'suppliers'

    def __str__(self):
        return self.company_name

class Products(models.Model):
    product_id = models.SmallIntegerField(primary_key=True)
    product_name = models.CharField(max_length=40)
    supplier = models.ForeignKey(Suppliers, models.DO_NOTHING, blank=True, null=True)
    category = models.ForeignKey(Categories, models.DO_NOTHING, blank=True, null=True)
    quantity_per_unit = models.CharField(max_length=20, blank=True, null=True)
    unit_price = models.FloatField(blank=True, null=True)
    units_in_stock = models.SmallIntegerField(blank=True, null=True)
    units_on_order = models.SmallIntegerField(blank=True, null=True)
    reorder_level = models.SmallIntegerField(blank=True, null=True)
    discontinued = models.IntegerField()
    date_discontinued = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'products'
    
    def __str__(self):
        return self.product_name
    
    @property
    def is_discontinued(self):
        return self.discontinued == 1

class Employees(models.Model):
    employee_id = models.SmallIntegerField(primary_key=True)
    last_name = models.CharField(max_length=20)
    first_name = models.CharField(max_length=10)
    title = models.CharField(max_length=30, blank=True, null=True)
    title_of_courtesy = models.CharField(max_length=25, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    hire_date = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=60, blank=True, null=True)
    city = models.CharField(max_length=15, blank=True, null=True)
    region = models.CharField(max_length=15, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    country = models.CharField(max_length=15, blank=True, null=True)
    home_phone = models.CharField(max_length=24, blank=True, null=True)
    extension = models.CharField(max_length=4, blank=True, null=True)
    photo = models.BinaryField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    reports_to = models.ForeignKey('self', models.DO_NOTHING, db_column='reports_to', blank=True, null=True)
    photo_path = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'employees'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Region(models.Model):
    region_id = models.SmallIntegerField(primary_key=True)
    region_description = models.CharField(max_length=60)

    class Meta:
        managed = False
        db_table = 'region'

    def __str__(self):
        return self.region_description

class Territories(models.Model):
    territory_id = models.CharField(primary_key=True, max_length=20)
    territory_description = models.CharField(max_length=60)
    region = models.ForeignKey(Region, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'territories'

    def __str__(self):
        return self.territory_description

class EmployeeTerritories(models.Model):
    employee = models.ForeignKey(Employees, models.DO_NOTHING, primary_key=True)
    territory = models.ForeignKey(Territories, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'employee_territories'
        unique_together = (('employee', 'territory'),)

class Shippers(models.Model):
    shipper_id = models.SmallIntegerField(primary_key=True)
    company_name = models.CharField(max_length=40)
    phone = models.CharField(max_length=24, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'shippers'

    def __str__(self):
        return self.company_name

class Orders(models.Model):
    order_id = models.SmallAutoField(primary_key=True)
    customer = models.ForeignKey(Customers, models.DO_NOTHING, blank=True, null=True)
    employee = models.ForeignKey(Employees, models.DO_NOTHING, blank=True, null=True)
    order_date = models.DateField(blank=True, null=True)
    required_date = models.DateField(blank=True, null=True)
    shipped_date = models.DateField(blank=True, null=True)
    ship_via = models.ForeignKey(Shippers, models.DO_NOTHING, db_column='ship_via', blank=True, null=True)
    freight = models.FloatField(blank=True, null=True)
    ship_name = models.CharField(max_length=40, blank=True, null=True)
    ship_address = models.CharField(max_length=60, blank=True, null=True)
    ship_city = models.CharField(max_length=15, blank=True, null=True)
    ship_region = models.CharField(max_length=15, blank=True, null=True)
    ship_postal_code = models.CharField(max_length=10, blank=True, null=True)
    ship_country = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'orders'

    def __str__(self):
        customer_name = self.customer.company_name if self.customer else "No Customer"
        return f"Order #{self.order_id} - {customer_name}"
    
    def get_order_total(self):
        """Calculate the total of all line items in this order"""
        from django.db.models import Sum
        
        # Get all order details for this order and sum up the line totals
        order_details = OrderDetails.objects.filter(order=self)
        total = 0
        for detail in order_details:
            total += detail.line_total
        return total
    
    @property
    def order_total(self):
        """Property to get the order total including freight"""
        subtotal = self.get_order_total()
        freight = self.freight or 0
        return subtotal + freight

class OrderDetails(models.Model):
    order = models.ForeignKey(Orders, models.DO_NOTHING, primary_key=True)
    product = models.ForeignKey(Products, models.DO_NOTHING)
    unit_price = models.FloatField()
    quantity = models.SmallIntegerField()
    discount = models.FloatField()

    class Meta:
        managed = False
        db_table = 'order_details'
        unique_together = (('order', 'product'),)

    def __str__(self):
        return f"Order #{self.order.order_id} - {self.product.product_name}"
    
    @property
    def line_total(self):
        """Calculate the line total for this order detail"""
        return self.unit_price * self.quantity * (1 - self.discount)

class UsStates(models.Model):
    state_id = models.SmallIntegerField(primary_key=True)
    state_name = models.CharField(max_length=100, blank=True, null=True)
    state_abbr = models.CharField(max_length=2, blank=True, null=True)
    state_region = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'us_states'

    def __str__(self):
        return self.state_name or f"State {self.state_id}"