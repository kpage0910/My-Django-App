# cart_utils.py
# Shopping cart utilities for managing session-based cart functionality

from decimal import Decimal
from .models import Products

def get_cart(request):
    """
    Get the current cart from the session.
    
    Returns:
        dict: Cart dictionary with product_id as keys and quantities as values
    """
    cart = request.session.get('cart', {})
    return cart


def add_to_cart(request, product_id, quantity=1):
    """
    Add a product to the cart. If the product is already in the cart,
    increment the quantity by the specified amount.
    
    Args:
        request: HTTP request object with session
        product_id: ID of the product to add
        quantity: Number of items to add (default: 1)
    
    Returns:
        dict: Updated cart
    """
    cart = get_cart(request)
    
    # Convert product_id to string for dictionary key
    product_id_str = str(product_id)
    
    # If product already in cart, add to existing quantity
    if product_id_str in cart:
        cart[product_id_str] += quantity
    else:
        cart[product_id_str] = quantity
    
    # Save cart back to session
    request.session['cart'] = cart
    request.session.modified = True
    
    return cart


def remove_from_cart(request, product_id):
    """
    Remove a product from the cart completely.
    
    Args:
        request: HTTP request object with session
        product_id: ID of the product to remove
    
    Returns:
        dict: Updated cart
    """
    cart = get_cart(request)
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart
        request.session.modified = True
    
    return cart


def update_cart_quantity(request, product_id, quantity):
    """
    Update the quantity of a specific product in the cart.
    Remove the item if quantity is 0 or less.
    
    Args:
        request: HTTP request object with session
        product_id: ID of the product to update
        quantity: New quantity
    
    Returns:
        dict: Updated cart
    """
    cart = get_cart(request)
    product_id_str = str(product_id)
    
    if quantity > 0:
        cart[product_id_str] = quantity
    elif product_id_str in cart:
        del cart[product_id_str]
    
    request.session['cart'] = cart
    request.session.modified = True
    
    return cart


def clear_cart(request):
    """
    Clear all items from the cart.
    
    Args:
        request: HTTP request object with session
    """
    request.session['cart'] = {}
    request.session.modified = True


def get_cart_items(request):
    """
    Get all items in the cart with full product details.
    
    Returns:
        dict: {
            'items': List of cart items with product details and line totals,
            'total': Total cart value,
            'count': Total number of items in cart
        }
    """
    cart = get_cart(request)
    items = []
    total = Decimal('0.00')
    count = 0
    
    for product_id_str, quantity in cart.items():
        try:
            product = Products.objects.get(product_id=int(product_id_str))
            
            # Skip discontinued products
            if product.discontinued == 1:
                continue
            
            line_total = Decimal(str(product.unit_price)) * quantity
            
            items.append({
                'product': product,
                'quantity': quantity,
                'line_total': line_total,
                'product_id': product.product_id
            })
            
            total += line_total
            count += quantity
            
        except Products.DoesNotExist:
            # Product no longer exists, skip it
            continue
    
    return {
        'items': items,
        'total': total,
        'count': count
    }


def validate_cart(request):
    """
    Validate cart contents - remove discontinued products.
    
    Args:
        request: HTTP request object with session
    
    Returns:
        list: List of product names that were removed (discontinued)
    """
    cart = get_cart(request)
    removed_products = []
    updated_cart = {}
    
    for product_id_str, quantity in cart.items():
        try:
            product = Products.objects.get(product_id=int(product_id_str))
            
            # Only keep non-discontinued products
            if product.discontinued == 0:
                updated_cart[product_id_str] = quantity
            else:
                removed_products.append(product.product_name)
                
        except Products.DoesNotExist:
            # Product doesn't exist, remove it
            pass
    
    # Update cart if items were removed
    if len(updated_cart) != len(cart):
        request.session['cart'] = updated_cart
        request.session.modified = True
    
    return removed_products