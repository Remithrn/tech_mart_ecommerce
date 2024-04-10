from random import randint
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from cartapp.models import Cart
from .models import Order, OrderItem
from customer.forms import AddressForm, AddressSelectForm
from orders.forms import PaymentMethodForm
from django.contrib.auth.decorators import login_required
import uuid
from datetime import datetime, timedelta
from cartapp.models import Cart, CartItem, Coupons, UserCoupons
import razorpay
from django.conf import settings
from customer.models import Wallet
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

from django.db import transaction


def generate_transaction_id():
    # Create a unique identifier using UUID
    transaction_id = str(uuid.uuid4())

    # Include a timestamp to make it time-specific
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    # Combine timestamp and UUID to form a unique transaction ID
    final_transaction_id = f"{timestamp}_{transaction_id}"

    return final_transaction_id[:8]




@login_required
def checkout(request):
    customer = request.user
    cart = Cart.objects.get(user=customer)
    total_amount = cart.get_total()
    total_discount = 0
    new_address = None
    for item in cart.cart_items.all():
        if item.quantity > item.product.stock:
            messages.error(request, f"Product {item.product.name} is out of stock")
            item.delete()
            return redirect("shop:home")

    if request.method == "POST":
        if cart.coupon:
            cart.coupon.redeemed_by.is_used = True
            cart.coupon.save()
            if cart.coupon_is_valid():
                total_amount = cart.total_after_coupon()
                total_discount = (
                    cart.get_total() - cart.total_after_coupon()
                ) + cart.get_total_discount()
            else:
                total_discount = 0
            UserCoupons.objects.create(user=customer, coupon=cart.coupon, is_used=True)
            cart.coupon = None
            cart.save()

       
        form_pay = PaymentMethodForm(request.POST)
        a_form = AddressSelectForm(request.POST, user=customer)

        if a_form.is_valid() and form_pay.is_valid():
            address = a_form.cleaned_data.get("address")

            if address is not None:
                new_address = str(address)
            elif form.is_valid():
                form.instance.user = customer
                new_address = f"{form.cleaned_data.get('street_address')}, {form.cleaned_data.get('city')}, {form.cleaned_data.get('state')}, {form.cleaned_data.get('zip_code')}"
                form.save()

            payment_method = form_pay.cleaned_data.get("payment_method")
            if payment_method =="Cash On Delivery" and total_amount >1000:
                messages.error(request, "Cash on delivery is only available for orders less than 1000")
                return redirect("cart:view_cart")

            with transaction.atomic():
                # Check item quantity again before creating order
                for item in cart.cart_items.all():
                    if item.quantity > item.product.stock:
                        messages.error(request, f"Product {item.product.name} is out of stock")
                        item.delete()
                        return redirect("shop:home")

                order = Order.objects.create(
                    customer=customer,
                    delivery_address=new_address,
                    payment_method=payment_method,
                    total_price=total_amount,
                    total_discount=total_discount,
                )

                for item in cart.cart_items.all():
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.total(),
                    )
                    item.product.stock -= item.quantity
                    item.product.save()
                    if item.product.price_after_discount() < item.product.price:
                        order.total_discount += (
                            item.product.price - item.product.price_after_discount()
                        )*item.quantity
                        order.save()
                         

                # Clear the cart after successful order creation
                cart.cart_items.all().delete()

                if payment_method == "Wallet":
                    wallet = Wallet.objects.get(customer=customer)
                    if wallet.balance < total_amount:
                        messages.error(request, "Insufficient Balance")
                        return redirect("orders:checkout")

                    wallet.balance -= total_amount
                    wallet.save()
                    order.payment_status = "Paid"
                    order.save()
                    messages.success(request, "Order placed successfully!")
                    return redirect("shop:home")

                if payment_method == "Razorpay":
                    client = razorpay.Client(
                        auth=(settings.RAZORPAY_KEY_ID, settings.KEY_SECRET)
                    )
                    payment = client.order.create(
                        {
                            "amount": float(order.total_price) * 100,
                            "currency": "INR",
                            "payment_capture": 1,
                        }
                    )
                    order.razorpay_payment_id = payment["id"]
                    order.save()
                    context = {"order": order, "payment": payment}
                    return render(request, "orders/razorpay_payment.html", context)
                elif payment_method == "Cash On Delivery":
                    order.payment_method = "Cash On Delivery"
                    order.save()
                    messages.success(request, "Order placed successfully!")
                    return redirect("shop:home")

            messages.success(request, "Order placed successfully!")
            return redirect("shop:home")

    else:
        a_form = AddressSelectForm(user=customer)
        
        form_pay = PaymentMethodForm()

    return render(
        request,
        "orders/place_order.html",
        { "form_payt": form_pay, "customer": customer, "a_form": a_form},
    )


@login_required
def payment_success(request, id):
    order = get_object_or_404(Order, razorpay_payment_id=id)
    order.payment_status = "Paid"
    order.payment_method = "Razorpay"

    order.save()
    messages.success(request, "Payment Successful")
    return redirect("shop:home")


@login_required
def payment_failed(request, id):
    order = get_object_or_404(Order, razorpay_payment_id=id)
    order.payment_status = "Failed"
    order.payment_method = "Razorpay"
    order.save()
    messages.error(request, "Payment Failed, please try again from profile page")
    return redirect("shop:home")


@login_required
def cancel_order(request, id):
    order = get_object_or_404(Order, id=id)

    if order.payment_status == "Paid" and not order.is_returned:
        wallet, created = Wallet.objects.get_or_create(customer=order.customer)
        wallet.balance = wallet.balance + order.total_price
        wallet.save()
        with transaction.atomic():
            for item in order.order_items.all():
                item.product.stock += item.quantity
                item.product.save()
            order.is_cancelled = True
            order.save()
            # Refund logic goes here
            messages.success(request, "Order cancelled successfully and refunded")
    elif order.payment_status != "Paid":
        wallet, created = Wallet.objects.get_or_create(customer=order.customer)
        wallet.balance = wallet.balance + order.total_price
        wallet.save()
        with transaction.atomic():
            for item in order.order_items.all():
                item.product.stock += item.quantity
                item.product.save()
            order.is_cancelled = True
            order.save()
        messages.success(request, "Order cancelled successfully")
    elif order.is_returned:
        messages.error(request, "Order has already been returned")
    else:
        messages.error(request, "Cannot cancel order")

    return redirect("customer:profile")


@login_required
def order_details(request, id):
    order = get_object_or_404(Order, id=id)
    order_items = OrderItem.objects.filter(order=order)
    return render(
        request,
        "orders/order_details.html",
        {"order": order, "order_items": order_items},
    )


@login_required
def return_order(request, id):
    order = get_object_or_404(Order, id=id)
    wallet, created = Wallet.objects.get_or_create(customer=request.user)
    if order.delivery_status != "Delivered":
        messages.error(request, "Order has not been delivered yet")
        return redirect("customer:profile")
   

    if order.is_returned:
        messages.error(request, "Order has already been returned")
    elif order.is_cancelled:
        messages.error(request, "Order has already been cancelled")
    elif order.payment_status != "Paid":
        order.is_returned = True
        order.save()
        messages.error(request, "Order is returned.")
        
    elif order.delivery_date and order.delivery_date + timedelta(days=3) < timezone.now():
        messages.error(request, "Cannot return order after 3 days")
    else:
        for item in order.order_items.all():
            item.product.stock += item.quantity
            item.product.save()
        wallet.balance += order.total_price
        wallet.save()
        order.is_returned = True
        order.save()
        messages.success(
            request, f"Return successful. Wallet credited with {order.total_price}"
        )

    return redirect("customer:profile")


@login_required
def view_wallet(request):
    wallet, created = Wallet.objects.get_or_create(customer=request.user)
    wallet_balance = wallet.balance
    wallet_orders = Order.objects.filter(customer=request.user, payment_method="Wallet").order_by('-date_ordered')

    paginator = Paginator(wallet_orders, 5)  # Show 10 orders per page

    page_number = request.GET.get('page')
    try:
        wallet_orders = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        wallet_orders = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        wallet_orders = paginator.page(paginator.num_pages)

    return render(request, "orders/wallet.html", {"wallet": wallet_balance, "wallet_order": wallet_orders})


@login_required
def change_payment_method(request,order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.payment_status == "Paid":
        messages.error(request, "Order has already been paid")
        return redirect("customer:profile")
    elif order.is_cancelled:
        messages.error(request, "Order has already been cancelled")
        return redirect("customer:profile")
    elif order.is_returned:
        messages.error(request, "Order has already been returned")
        return redirect("customer:profile")

    if request.method == "POST":
        form = PaymentMethodForm(request.POST)
        if form.is_valid():
            user = request.user
            user.payment_method = form.cleaned_data["payment_method"]
            if user.payment_method == "Wallet":
                    wallet = Wallet.objects.get(customer= user)
                    if wallet.balance < order.total_price:
                        messages.error(request, "Insufficient Balance")
                        return redirect("customer:profile")

                    wallet.balance -= order.total_price
                    wallet.save()
                    order.payment_status = "Paid"
                    order.payment_method = "Wallet"
                    order.save()
                    messages.success(request, "Order placed successfully!")
                    return redirect("shop:home")

            elif user.payment_method == "Razorpay":
                    client = razorpay.Client(
                        auth=(settings.RAZORPAY_KEY_ID, settings.KEY_SECRET)
                    )
                    payment = client.order.create(
                        {
                            "amount": float(order.total_price) * 100,
                            "currency": "INR",
                            "payment_capture": 1,
                        }
                    )
                    order.razorpay_payment_id = payment["id"]
                    order.save()
                    context = {"order": order, "payment": payment}
                    return render(request, "orders/razorpay_payment.html", context)
            elif user.payment_method == "Cash On Delivery":
                if order.total_price >1000:
                    messages.error(request, "Cash on Delivery only for orders less than Rs.1000")
                    return redirect("shop:home")
                else:                    
                    order.payment_method = "Cash On Delivery"
                order.save()
                

            messages.success(request, "Order placed successfully!")
            return redirect("shop:home")            
          
    else:
        form = PaymentMethodForm()
    return render(request, "orders/change_payment_method.html", {"form": form})
    


