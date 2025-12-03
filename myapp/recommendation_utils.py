"""
Product recommendation utilities for suggesting products based on customer purchasing patterns.
"""

from django.db.models import Count, Sum, Q
from .models import OrderDetails, Products


def get_product_recommendations(customer, limit=10):
    """
    Generate product recommendations for a customer based on collaborative filtering.
    
    Algorithm:
    1. Find products the customer has already purchased
    2. Find other customers who bought the same products (similar customers)
    3. Find products those similar customers bought
    4. Exclude products the customer already owns and discontinued products
    5. Rank by purchase frequency among similar customers
    
    Args:
        customer: Customers model instance
        limit: Maximum number of recommendations to return (default: 10)
    
    Returns:
        QuerySet of Products with annotations for purchase_count and customer_count
    """
    
    # Get all products this customer has purchased
    customer_products = OrderDetails.objects.filter(
        order__customer=customer
    ).values_list('product_id', flat=True).distinct()
    
    # If customer has no purchase history, return top-selling products overall
    if not customer_products:
        top_sellers = Products.objects.filter(
            discontinued=0
        ).annotate(
            purchase_count=Count('orderdetails__order', distinct=True),
            total_quantity=Sum('orderdetails__quantity')
        ).filter(
            purchase_count__gt=0
        ).order_by('-purchase_count', '-total_quantity')[:limit]
        
        return top_sellers
    
    # Find customers who bought the same products (similar customers)
    similar_customers = OrderDetails.objects.filter(
        product_id__in=customer_products
    ).values('order__customer').annotate(
        shared_products=Count('product', distinct=True)
    ).exclude(
        order__customer=customer
    ).order_by('-shared_products')[:50]  # Top 50 similar customers
    
    similar_customer_ids = [item['order__customer'] for item in similar_customers]
    
    # If no similar customers found, return top sellers
    if not similar_customer_ids:
        top_sellers = Products.objects.filter(
            discontinued=0
        ).exclude(
            product_id__in=customer_products
        ).annotate(
            purchase_count=Count('orderdetails__order', distinct=True),
            total_quantity=Sum('orderdetails__quantity')
        ).filter(
            purchase_count__gt=0
        ).order_by('-purchase_count', '-total_quantity')[:limit]
        
        return top_sellers
    
    # Get products purchased by similar customers
    # Exclude products customer already bought and discontinued products
    recommendations = Products.objects.filter(
        orderdetails__order__customer_id__in=similar_customer_ids
    ).exclude(
        product_id__in=customer_products
    ).filter(
        discontinued=0
    ).annotate(
        purchase_count=Count('orderdetails__order', distinct=True),
        customer_count=Count('orderdetails__order__customer', distinct=True),
        total_quantity=Sum('orderdetails__quantity')
    ).order_by('-purchase_count', '-customer_count', '-total_quantity')[:limit]
    
    return recommendations
