# contextUtilities.py
# Context processors to make cart data available in all templates

from .cart_utils import get_cart_items


def cart_context(request):
    """
    Context processor to add cart information to all templates.
    This makes cart data available in base.html and all templates that extend it.
    
    Returns:
        dict: Context dictionary with cart information
    """
    cart_data = get_cart_items(request)
    
    return {
        'cart_count': cart_data['count'],
        'cart_total': cart_data['total'],
        'cart_items': cart_data['items']
    }