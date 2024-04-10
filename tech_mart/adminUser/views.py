from django.shortcuts import render, redirect, get_object_or_404
from .forms import AdminCreationForm, OrdersForm
from django.contrib import messages
from shop.forms import ProductForm, CategoryForm, ProductImageForm
from customer.models import Customer
from shop.models import Product, Category, ProductImage
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.cache import never_cache
from django.views import View
from orders.models import Order, OrderItem
from django.utils import timezone
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from django.db.models import F
from cartapp.models import Coupons, UserCoupons
from cartapp.forms import CouponForm
from django.shortcuts import render
from django.db.models import Sum, Count, Case, When, IntegerField
from django.db.models.functions import ExtractYear, ExtractMonth, ExtractDay, TruncDate
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from datetime import date, datetime, timedelta
import csv
from reportlab.lib.pagesizes import letter
from django.http import HttpResponse, JsonResponse
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.units import inch
from reportlab.platypus import Spacer
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@never_cache
def adminRegistration(request):
    if request.user.is_authenticated:
        return redirect("customer:dashboard")
    form = AdminCreationForm()
    if request.method == "POST":
        form = AdminCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "admin user created successfully!!")
            return redirect("customer:login")
        else:
            messages.error(request, form.errors)
            return redirect("adminUser:adminregistration")
    return render(request, "adminUser/register.html", {"form": form})


@user_passes_test(lambda u: u.is_superuser, login_url="adminUser:error")
@never_cache
def adminDashboard(request):
    users = Customer.objects.all()
    products = Product.objects.all()
    categories = Category.objects.all()
    orders = Order.objects.all()

    context = {
        "users": users,
        "products": products,
        "categories": categories,
        "orders": orders,
    }

    return render(request, "adminUser/dashboard.html", context)


@user_passes_test(lambda u: u.is_superuser, login_url="adminUser:error")
@never_cache
def toggle_customer_status(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    if customer.is_active:
        customer.is_active = False
        customer.save()
        messages.success(request, "Customer deactivated successfully.")
    else:
        customer.is_active = True
        customer.save()
        messages.success(request, "Customer activated successfully.")
    return redirect("adminUser:dashboard")


@user_passes_test(lambda u: u.is_superuser, login_url="adminUser:error")
@never_cache
def create_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created successfully.")
            return redirect("adminUser:categories")
        else:
            messages.error(request, form.errors)
    else:
        form = CategoryForm()

    return render(request, "adminUser/create_category.html", {"form": form})


@user_passes_test(lambda u: u.is_superuser, login_url="adminUser:error")
@never_cache
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    form = CategoryForm()
    if request.method == "POST":
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "updated successfully")
            return redirect("adminUser:categories")
    else:
        form = CategoryForm(instance=category)
        messages.error(request, form.errors)

    return render(request, "adminUser/edit.html", {"form": form, "model": "Category"})


@user_passes_test(lambda u: u.is_superuser, login_url="adminUser:error")
@never_cache
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    productform = ProductForm(instance=product)
    imageform = ProductImageForm()

    if request.method == "POST":
        productform = ProductForm(request.POST, request.FILES, instance=product)

        if productform.is_valid():
            product = productform.save(commit=False)
            product.save()

            # If images are provided, update them; otherwise, keep the old ones
            if request.FILES.getlist("images"):
                # check if files are images
                for file in request.FILES.getlist("images"):
                    if file.content_type not in ["image/jpeg", "image/png", "image/gif", "image/svg+xml", "image/webp"]:
                        messages.error(request, "Only images are allowed.")
                        return render(request, "adminUser/create_new.html", {"p_form": productform, "i_form": imageform, "operation": "update", "product": product})
                # Delete old images if needed
                product.images.all().delete()

                # Create new images
                for file in request.FILES.getlist("images"):
                    ProductImage.objects.create(product=product, image=file)

            messages.success(request, "Product updated successfully")
            return redirect("adminUser:products")
        else:
            messages.error(request, productform.errors)

    context = {
        "p_form": productform,
        "i_form": imageform,
        "operation": "update",
        "product": product,
    }
    return render(request, "adminUser/create_new.html", context)


@user_passes_test(lambda u: u.is_superuser, login_url="adminUser:error")
@never_cache
def user_management(request):
    users_list = Customer.objects.all()
    paginator = Paginator(users_list, 10)  # Show 10 users per page

    page = request.GET.get("page")
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        users = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        users = paginator.page(paginator.num_pages)

    return render(request, "adminUser/user_management.html", {"users": users})


@user_passes_test(lambda u: u.is_superuser, login_url="adminUser:error")
@never_cache
def product_management(request):
    products_list = Product.objects.all()
    paginator = Paginator(products_list, 10)  # Show 10 products per page

    page = request.GET.get("page")
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        products = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        products = paginator.page(paginator.num_pages)

    return render(request, "adminUser/product_management.html", {"products": products})


@user_passes_test(lambda u: u.is_superuser, login_url="adminUser:error")
@never_cache
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    try:
        category.delete()
        messages.success(request, "Deleted category successfully.")
    except Exception as e:
        messages.error(request, f"Error deleting category: {e}")

    return redirect("adminUser:categories")


@user_passes_test(lambda u: u.is_superuser, login_url="error")
@never_cache
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        product.delete()
        messages.success(request, "Deleted product successfully.")
    except Exception as e:
        messages.error(request, f"Error deleting product: {e}")

    return redirect("adminUser:products")


def error_view(request):
    messages.error(request, "only admims are authorised for this function")
    return redirect("shop:home")


@user_passes_test(lambda u: u.is_superuser, login_url="error")
@never_cache
def create_product12(request):
    productform = ProductForm()
    imageform = ProductImageForm()

    if request.method == "POST":

        files = request.FILES.getlist("images")
        for file in files:
            if file.content_type not in ["image/jpeg", "image/png", "image/gif", "image/svg+xml", "image/webp"]:
                        messages.error(request, "Only images are allowed.")
                        return render(request, "adminUser/create_new.html", {"p_form": productform, "i_form": imageform, "operation": "create"})
                        
        

        productform = ProductForm(request.POST, request.FILES)
        if productform.is_valid():
            product = productform.save(commit=False)

            product.save()
            messages.success(request, "Product created successfully")

            for file in files:

                ProductImage.objects.create(product=product, image=file)
                

            return redirect("adminUser:products")
        else:
            messages.error(request, productform.errors)

    context = {"p_form": productform, "i_form": imageform, "operation": "create"}
    return render(request, "adminUser/create_new.html", context)

@user_passes_test(lambda u: u.is_superuser, login_url="adminUser:error")
@never_cache
def category_management(request):
    categories = Category.objects.all()
    return render(
        request, "adminUser/category_management.html", {"categories": categories}
    )


@user_passes_test(lambda u: u.is_superuser, login_url="adminUser:error")
@never_cache
def order_management(request):
    orders_list = Order.objects.all()
    paginator = Paginator(orders_list, 9)  # Show 10 orders per page

    page = request.GET.get("page")
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        orders = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        orders = paginator.page(paginator.num_pages)

    return render(request, "adminUser/order_management.html", {"orders": orders})

@user_passes_test(lambda u: u.is_superuser, login_url="adminUser:error")
@never_cache
def edit_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if request.method == "POST":
        form = OrdersForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            if order.delivery_status == "Delivered":
                order.delivery_date = datetime.now()
                messages.success(request, "Order delivered successfully")

            return redirect("adminUser:orders")
    else:
        form = OrdersForm(instance=order)  # Pre-fill form for editing
    return render(request, "adminUser/edit_order.html", {"form": form})


@user_passes_test(lambda u: u.is_superuser, login_url='/login/')
def sales_report(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    date_range = request.GET.get("date_range")
    range_used = False

    if date_range:
        range_used = True
        today = date.today()
        if date_range == "1day":
            start_date = end_date = today
        elif date_range == "1week":
            start_date = today - timedelta(days=7)
            end_date = today
        elif date_range == "1month":
            start_date = today - timedelta(days=30)
            end_date = today
        elif date_range == "1year":
            start_date = today - timedelta(days=365)
            end_date = today
            print(start_date)
            print(end_date)

    if not start_date:
        start_date = date.today()
    if not end_date:
        end_date = date.today()

    orders = Order.objects.filter(
        date_ordered__range=[start_date, end_date],
        is_cancelled=False,
        is_returned=False
    )

    total_orders = orders.count()
    total_revenue = orders.aggregate(total_price=Sum('total_price', default=0))['total_price']
    total_discount = orders.aggregate(total_discount=Sum('total_discount', default=0))['total_discount']

    pending_payment_orders = orders.filter(payment_status="Pending")
    pending_payment = pending_payment_orders.aggregate(total_price=Sum('total_price', default=0))['total_price']

    revenue_by_payment = orders.values('payment_method').annotate(total=Sum('total_price')).order_by('-total')

    top_products = OrderItem.objects.filter(order__in=orders).values('product__name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:10]
    top_categories = OrderItem.objects.filter(order__in=orders).values('product__category__name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:10]
    top_brands = OrderItem.objects.filter(order__in=orders).values('product__brand__name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:10]
    revenue_over_time = orders.annotate(date=TruncDate('date_ordered')).values('date').annotate(total_price=Sum('total_price')).order_by('date')

    total_by_razorpay = orders.filter(payment_method="Razorpay").aggregate(total_price=Sum('total_price', default=0))['total_price']

    context = {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_discount': total_discount,
        'revenue_by_payment': revenue_by_payment,
        'top_products': top_products,
        'revenue_over_time': revenue_over_time,
        'start_date': start_date,
        'end_date': end_date,
        'range_used': range_used,
        'pending_payment': pending_payment,
        'total_by_razorpay': total_by_razorpay,
        'top_categories': top_categories,
        'top_brands': top_brands
    }

    if request.GET.get("download"):
        download_type = request.GET.get("download")
        if download_type == "pdf":
            return generate_pdf_report(orders, total_revenue, total_discount)
        elif download_type == "excel":
            return generate_excel_report(orders, total_revenue, total_discount)

    return render(request, "adminUser/sales_report.html", context)
def generate_pdf_report(orders, total_revenue, total_discount):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="orders.pdf"'

    pdf_buffer = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    heading_style = ParagraphStyle(name="Heading", fontSize=18, alignment=1)
    heading = Paragraph(f"Sales Report from ", heading_style)
    elements.append(heading)

    elements.append(Spacer(1, 0.5 * inch))

    table_data = [
        [
            "Order ID",
            "User",
            "Total Price",
            "Order Date",
            "Payment Status",
            "Delivery Status",
            "Payment Type",
        ]
    ]
    for order in orders:
        order_data = [
            order.id,
            order.customer.username,
            f"${order.total_price}",
            order.date_ordered.date(),
            order.payment_status,
            order.delivery_status,
            order.payment_method,
        ]
        table_data.append(order_data)
    table_data.append(["Total", "", f"${total_revenue}", "", "", "", ""])
    table_data.append(["Discount", "", f"${total_discount}", "", "", "", ""])

    order_table = Table(table_data)
    order_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )

    elements.append(order_table)
    pdf_buffer.build(elements)

    return response


def generate_excel_report(orders, total_revenue, total_discount):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="orders.csv"'
    writer = csv.writer(response)
    writer.writerow(
        [
            "Order ID",
            "User",
            "Total Price",
            "Order Date",
            "Payment Status",
            "Delivery Status",
            "Payment Type",
        ]
    )
    for order in orders:
        writer.writerow(
            [
                order.id,
                order.customer.username,
                f"${order.total_price}",
                order.date_ordered.date(),
                order.payment_status,
                order.delivery_status,
                order.payment_method,
            ]
        )
    writer.writerow(["Total", "", f"${total_revenue}", "", "", "", ""])
    writer.writerow(["Discount", "", f"${total_discount}", "", "", "", ""])
    return response

@user_passes_test(lambda u: u.is_superuser, login_url="adminUser:error")
def coupon_management(request):
    coupons = Coupons.objects.all()
    context = {"coupons": coupons}
    return render(request, "adminUser/coupons_list.html", context)

@user_passes_test(lambda u: u.is_superuser, login_url="adminUser:error")
def create_coupon(request):
    if request.method == "POST":
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Coupon created successfully!")
            return redirect("adminUser:coupons")
        else:
            messages.error(request, form.errors)
    else:
        form = CouponForm()
    return render(
        request, "adminUser/create_coupon.html", {"form": form, "operation": "Create"}
    )


@user_passes_test(lambda u: u.is_superuser, login_url="adminUser:error")
@never_cache
def edit_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupons, id=coupon_id)
    if request.method == "POST":
        form = CouponForm(request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            messages.success(request, "Coupon updated successfully!")
            return redirect("adminUser:coupons")
        else:
            messages.error(request, form.errors)
    else:
        form = CouponForm(instance=coupon)
    return render(
        request, "adminUser/create_coupon.html", {"form": form, "operation": "Edit"}
    )

@user_passes_test(lambda u: u.is_superuser, login_url="adminUser:error")
@never_cache
def delete_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupons, id=coupon_id)
    coupon.delete()
    messages.success(request, "Coupon deleted successfully!")
    return redirect("adminUser:coupons")
