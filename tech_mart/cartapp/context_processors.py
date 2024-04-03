from .models import Cart, CartItem


def counter(request):
    cart_count = 0
    try:

        if request.user.is_authenticated:
            user = request.user
            cart, _ = Cart.objects.get_or_create(user=user)
            cart_items = CartItem.objects.all().filter(cart=cart)
        try:
            for cart_item in cart_items:
                cart_count += cart_item.quantity
        except:
            cart_count = 0
    except Cart.DoesNotExist:
        cart_count = 0
    return {"cart_count": cart_count}
