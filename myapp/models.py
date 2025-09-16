# myapp/models.py
from django.db import models


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

    # Meta information
    class Meta:
        managed = False
        db_table = 'customers'

    # String representation
    def __str__(self):
        return f"{self.company_name} - {self.contact_name}"

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

class Products(models.Model):
    product_id = models.SmallIntegerField(primary_key=True)
    product_name = models.CharField(max_length=40)
    category = models.ForeignKey(Categories, models.DO_NOTHING, blank=True, null=True)
    quantity_per_unit = models.CharField(max_length=20, blank=True, null=True)
    unit_price = models.FloatField(blank=True, null=True)
    units_in_stock = models.SmallIntegerField(blank=True, null=True)
    units_on_order = models.SmallIntegerField(blank=True, null=True)
    reorder_level = models.SmallIntegerField(blank=True, null=True)
    discontinued = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'products'
    
    def __str__(self):
        return self.product_name
    
    @property
    def is_discontinued(self):
        return self.discontinued == 1

class Orders(models.Model):
    order_id = models.SmallIntegerField(primary_key=True)
    customer = models.ForeignKey(Customers, models.DO_NOTHING, blank=True, null=True)
    order_date = models.DateField(blank=True, null=True)
    required_date = models.DateField(blank=True, null=True)
    shipped_date = models.DateField(blank=True, null=True)
    freight = models.FloatField(blank=True, null=True)
    ship_name = models.CharField(max_length=40, blank=True, null=True)
    ship_address = models.CharField(max_length=60, blank=True, null=True)
    ship_city = models.CharField(max_length=15, blank=True, null=True)
    ship_country = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'orders'

class OrderDetails(models.Model):
    order = models.ForeignKey('Orders', models.DO_NOTHING)
    product = models.ForeignKey('Products', models.DO_NOTHING)
    unit_price = models.FloatField()
    quantity = models.SmallIntegerField()
    discount = models.FloatField()

    class Meta:
        managed = False
        db_table = 'order_details'