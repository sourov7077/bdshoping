from .cart import Cart

def cart_total(request):
    cart = Cart(request)
    return {
        'cart_total_items': cart.get_total_items(),
        'cart_total_price': cart.get_total_price(),
    }