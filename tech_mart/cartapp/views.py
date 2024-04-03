from django.shortcuts import render,redirect,get_object_or_404
from shop.models import Product
from customer.models import Customer
from .models import Cart,CartItem, Coupons, UserCoupons, Wishlist
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from orders.models import Order, OrderItem
from customer.forms import AddressForm
from.forms import CouponApplyForm
from django.utils import timezone
# Create your views here.


@login_required
def add_cart(request, slug):
    product=Product.objects.get(slug=slug)
    user=request.user
    cart,_=Cart.objects.get_or_create(user=user)
    cart.save()
    cart_items=CartItem.objects.filter(cart=cart,product=product).first()
    if cart_items:
        if cart_items.quantity < product.stock:
            cart_items.quantity+=1
            cart_items.save()
        else:
            messages.error(request, "Product is out of stock")
        
        
    else:
        cart_items=CartItem.objects.create(cart=cart,product=product,quantity=1)
        cart_items.save()
    return redirect('cart:view_cart')
@login_required
def remove_item(request, slug):
    product=Product.objects.get(slug=slug)
    user=request.user
    cart,_=Cart.objects.get_or_create(user=user)
    cart_items=CartItem.objects.filter(cart=cart,product=product).first()
    if cart_items:
        if cart_items.quantity > 1:
            cart_items.quantity -= 1
            cart_items.save()
        else:
            cart_items.delete()
    return redirect('cart:view_cart') 
@login_required
def remove_all_item(request, slug):
    product=Product.objects.get(slug=slug)
    user=request.user
    cart,_=Cart.objects.get_or_create(user=user)
    cart_items=CartItem.objects.filter(cart=cart,product=product).first()
    if cart_items:
        cart_items.delete()
    return redirect('cart:view_cart')    
@login_required
def cart_view(request):
    user=request.user
    cart,_=Cart.objects.get_or_create(user=user)
    print(cart)
    cart_items=CartItem.objects.filter(cart=cart)
    form = CouponApplyForm()
    if request.method == 'POST':
        form = CouponApplyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                coupon = Coupons.objects.get(coupon_code__iexact=code, is_expired=False)
            except Coupons.DoesNotExist:
                messages.error(request, 'Invalid coupon code')
            else:
                if coupon.is_used_by_user(request.user):
                    messages.error(request, 'You have already used this coupon')
                elif cart.get_subtotal() < coupon.minimum_amount:
                    messages.error(request, f'Minimum order value for this coupon is {coupon.minimum_amount}')
                elif coupon.valid_to < timezone.now():
                    messages.error(request, 'Coupon is expired')
                else:
                    cart.coupon = coupon
                    cart.save()
                    
                    messages.success(request, 'Coupon applied successfully')
    
    context={
        'cart_items':cart_items,
        'cart':cart,
        'form':form
    }
    return render(request,'cartapp/cart.html',context)

def remove_coupon(request):
    user=request.user
    cart,_=Cart.objects.get_or_create(user=user)
    cart.coupon=None
    cart.save()
    messages.success(request, 'Coupon removed successfully')
    return redirect('cart:view_cart')
@login_required
def add_to_wishlist(request, slug):
    product=Product.objects.get(slug=slug)
    user = request.user
    wishlist_item, created = Wishlist.objects.get_or_create(user=user, product=product)

    if created:
        # Item added to wishlist
        pass
    else:
        # Item already in wishlist
        pass

    
    
    return redirect('shop:detail',slug=slug)
   
@login_required
def remove_from_wishlist(request, slug):
    product=Product.objects.get(slug=slug)
    user=request.user
    whishlist_item=Wishlist.objects.filter(user=user,product=product).first()
    whishlist_item.delete()
    return redirect('shop:detail',slug=slug)
@login_required
def whishlist(request):
    user=request.user
    whishlist_items=Wishlist.objects.filter(user=user)
    products=Product.objects.filter(wishlist__in=whishlist_items)
    print(products)
    for product in products:
        print(product.name)
    print(whishlist_items)
    
    context={
        'products':products
    }
    return render(request,'cartapp/wishlist.html',context)











