import re
from django.forms import ValidationError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Customer, Address
from .forms import CustomerRegistrationForm
import random
from .helper import MessageHandler
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from orders.models import Order, OrderItem
from cartapp.models import Cart, CartItem
from customer.forms import AddressForm, CuatomerEditForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, update_session_auth_hash
import secrets
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_POST


def generate_otp(length=6):
    """
    Generate a random OTP of the specified length.

    Parameters:
    - length: Length of the OTP (default is 6).

    Returns:
    A string representing the generated OTP.
    """
    otp = "".join(secrets.choice("0123456789") for _ in range(length))
    return otp


# Create your views here.


def registerView(request):
    form = CustomerRegistrationForm()

    if request.method == "POST":
        form = CustomerRegistrationForm(request.POST)

        if form.is_valid():
            messages.success(request, "Registration successful!")
            otp = generate_otp()

            customer = form.save(commit=False)
            customer.otp = otp
            customer.save()
            print(customer.id)
            red = redirect("customer:otp", customer.id)
            red.set_cookie("can_otp_enter", True, max_age=600)
            return red

        else:
            print(form.errors)
            messages.error(request, form.errors)

    return render(request, "customer/register.html", {"form": form})


def verifyOtp(request, id):

    if request.method == "POST":
        profile = Customer.objects.get(id=id)
        if request.COOKIES.get("can_otp_enter") is not None:
            if profile.otp == request.POST["otp"]:
                profile.is_verified = True
                profile.save(update_fields=["is_verified"])
                login(request, profile)
                red = redirect("shop:home")
                red.set_cookie("verified", True)
                return red
            messages.error(request, "Wrong OTP")
            return render(request, "customer/verify_otp.html", {"id": id})
        messages.error(request, "Wrong OTP")
        return render(request, "customer/verify_otp.html", {"id": id})
    return render(request, "customer/verify_otp.html", {"id": id})


def resendOtp(request, id):
    profile = Customer.objects.get(id=id)
    otp = generate_otp()
    profile.otp = otp
    profile.save(update_fields=["otp"])
    messages.success(request, "OTP resent")
    print(f"Generated OTP: {otp}")
    print(profile.id)
    red = redirect("customer:otp", profile.id)
    red.set_cookie("can_otp_enter", True, max_age=600)
    return red


def logout_view(request):
    logout(request)
    return redirect("shop:home")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("shop:home")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Hello {username}")
            return redirect("shop:home")
        else:
            messages.error(request, "Invalid credentials")
            return redirect("customer:login")

    return render(request, "customer/login.html")


@login_required
def profile_view(request):
    if request.user.is_authenticated:
        customer = Customer.objects.get(username=request.user.username)
        customer_addresses = Address.objects.filter(user=request.user)
        orders_list = Order.objects.filter(
            customer=customer, is_returned=False
        ).order_by("-date_ordered")
        paginator = Paginator(orders_list, 10)  # Show 10 orders per page

        page = request.GET.get("page")
        try:
            orders = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            orders = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            orders = paginator.page(paginator.num_pages)

        order_count = orders_list.count()
        total_orders = sum(order.total_price for order in orders_list)
        print(customer_addresses)
        return render(
            request,
            "customer/profile.html",
            {
                "customer": customer,
                "orders": orders,
                "order_count": order_count,
                "total_orders": total_orders,
                "customer_addresses": customer_addresses,
            },
        )


@login_required
def add_new_address(request):
    form = AddressForm()
    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, "Address added successfully!")
            return redirect("customer:profile")
        else:
            messages.error(request, form.errors)
            return redirect("customer:profile")

    return render(request, "customer/add_new_address.html", {"form": form})
@login_required
def edit_address(request, id):
    address = Address.objects.get(id=id)
    form = AddressForm(instance=address)
    if request.method == "POST":
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, "Address updated successfully!")
            return redirect("customer:profile")
        messages.error(request, form.errors)
    return render(request, "customer/edit_address.html", {"form": form})

@login_required
def delete_address(request, id):
    address = Address.objects.get(id=id)
    address.delete()
    messages.success(request, "Address deleted successfully!")
    return redirect("customer:profile")

        
    


from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError


@login_required
def change_password_view(request):
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("password1")
        confirm_password = request.POST.get("password2")
        print(current_password, new_password, confirm_password)

        try:
            # Validate the new password using Django's built-in password validators
            validate_password(new_password, request.user)

            # Check if new password matches the confirm password
            if new_password == confirm_password:
                # Authenticate user with current password
                user = authenticate(
                    username=request.user.username, password=current_password
                )
                if user is not None:
                    # Set new password and save user
                    user.set_password(new_password)
                    user.save()
                    # Update session auth hash to keep user logged in after password change
                    update_session_auth_hash(request, user)
                    messages.success(request, "Password changed successfully!")
                    return redirect("customer:profile")
                else:
                    messages.error(request, "Invalid credentials")
            else:
                messages.error(request, "Passwords do not match")
        except DjangoValidationError as e:
            # If new password validation fails, display error messages to the user
            for error in e.messages:
                messages.error(request, error)

        # If there's any error, or passwords don't match, redirect back to the change password page
        return redirect("customer:change_password")
    else:
        return render(request, "customer/change_password.html")


@login_required
def edit_profile_view(request):
    if request.method == "POST":
        form = CuatomerEditForm(request.POST, instance=request.user)
        form_address = AddressForm(request.POST, instance=request.user.address)

        if form.is_valid() and form_address.is_valid():
            form.save()

            address = form_address.save(commit=False)
            address.user = request.user
            address.save()

            messages.success(request, "Profile updated successfully!")
            return redirect("customer:profile")
        else:
            messages.error(request, form_address.errors)
            messages.error(request, form.errors)
            return redirect("customer:edit_profile")
    else:
        address = Address.objects.filter(user=request.user).first()
        customer = Customer.objects.get(username=request.user.username)

        if address:
            form_address = AddressForm(instance=address)
        else:
            form_address = AddressForm()

        form = CuatomerEditForm(instance=request.user)

    return render(
        request,
        "customer/edit_profile.html",
        {"form": form, "form_address": form_address},
    )


def check_username(request):
    form = CustomerRegistrationForm()
    if request.method == "POST":
        print('post')
        form = CustomerRegistrationForm(request.POST)
        username = request.POST.get("username")

        if not username:
            return HttpResponse("<span class='text-danger'>Username is required</span>")
        elif len(username) < 4:
            return HttpResponse(
                "<span class='text-danger'>Username must be at least 4 characters</span>"
            )

        elif Customer.objects.filter(username=username).exists():
            return HttpResponse(
                "<span class='text-danger'>Username already exists</span>"
            )
        else:
            return HttpResponse(
                "<span class = 'text-success'>Username available </span>"
            )
    return render(request, "customer/check_username.html", {"form": form})


@require_POST
def validate_passwords_view(request):
    if request.method == "POST":
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        try:
            validate_password(password1)

        except DjangoValidationError as e:
            err = ""
            for error in e.messages:
                err += "\n" + error

            return HttpResponse(f"<span class = 'text-danger'>{err}</span>")
        if password1 != password2:
            return HttpResponse(
                "<span class = 'text-danger'>Passwords do not match </span>"
            )
        return HttpResponse("<span class = 'text-success'>Passwords match </span>")


def test_register(request):
    form = CustomerRegistrationForm()
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            # Process the valid form data (e.g., save the user)
            return JsonResponse({'status': 'success'})
        else:
        # If the request method is not POST, or if the form is not valid, render the form with the provided data (if any)
            form = CustomerRegistrationForm(request.POST)
    
    return render(request, 'customer/check_username.html', {'form': form})