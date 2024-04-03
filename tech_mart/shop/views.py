from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from .models import Product, Category, ProductImage, Brand, Review
from .forms import ProductFilterForm, ReviewForm
from orders.models import Order, OrderItem
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# Create your views here.
class ProductList(ListView):
    model = Product
    context_object_name = "products"
    template_name = "shop/shop.html"
    paginate_by = 12  # Number of products per page


class ProductDetail(DetailView):
    model = Product
    template_name = "shop/product.html"
    context_object_name = "product"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the product's category
        product_category = self.object.category
        review_form = ReviewForm()
        can_add_review = False

        # Get other products of the same category (excluding the current product)
        related_products = Product.objects.filter(category=product_category).exclude(
            pk=self.object.pk
        )
        if self.request.user.is_authenticated:

            has_purchased = OrderItem.objects.filter(
                product=self.object,
                order__customer=self.request.user,
                order__delivery_status="Delivered",
            ).exists()

            has_left_a_review = Review.objects.filter(
                product=self.object, customer=self.request.user
            ).exists()
            can_add_review = has_purchased and not has_left_a_review
            context["has_purchased"] = has_purchased
            context["has_left_a_review"] = has_left_a_review

        context["related_products"] = related_products
        context["review_form"] = review_form
        context["can_add_review"] = can_add_review

        return context

    def post(self, request, *args, **kwargs):
        product = self.get_object()
        review_form = ReviewForm(request.POST)

        if review_form.is_valid():
            # Save the review to the database with the current user
            review = review_form.save(commit=False)
            review.customer = request.user
            review.product = product
            review.save()

            # Redirect back to the product detail page after submission
            messages.success(request, "Review submitted successfully")
            review_form = ReviewForm()
            return redirect("shop:detail", slug=product.slug)
        else:
            messages.error(request, "Error submitting review")

        # If the form is not valid, re-render the product detail page with the form and errors
        return render(
            request,
            self.template_name,
            {"product": product, "review_form": review_form},
        )


def home(request):
    return render(request, "base.html")


class ShopList(ListView):
    model = Product
    context_object_name = "products"
    template_name = "shop/category.html"


from django.core.paginator import Paginator, EmptyPage, InvalidPage


def allProdCat(request, c_slug=None):
    c_page = None
    products_list = None

    if c_slug is not None:
        c_page = get_object_or_404(Category, slug=c_slug)
        products_list = Product.objects.all().filter(category=c_page, available=True)
    else:
        products_list = Product.objects.all().filter(available=True)

    products = products_list

    return render(
        request, "shop/category.html", {"category": c_page, "products": products}
    )


def filter_product_list(request):
    form = ProductFilterForm(request.GET)
    products = Product.objects.all()

    if form.is_valid():
        if form.cleaned_data.get("price_min"):
            products = products.filter(price__gte=form.cleaned_data["price_min"])
        if form.cleaned_data.get("price_max"):
            products = products.filter(price__lte=form.cleaned_data["price_max"])
        if form.cleaned_data.get("brand"):
            products = products.filter(brand=form.cleaned_data["brand"])
        if form.cleaned_data.get("category"):
            products = products.filter(category=form.cleaned_data["category"])
        search_query = request.GET.get("search", "")
        if search_query:
            products = products.filter(name__icontains=search_query)

    paginator = Paginator(products, 10)  # Show 10 products per page
    page = request.GET.get("page")
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        products = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        products = paginator.page(paginator.num_pages)

    return render(request, "shop/category.html", {"form": form, "products": products})


@login_required
def edit_review(request, pk):
    review = get_object_or_404(Review, pk=pk, customer=request.user)

    if request.method == "POST":
        review_form = ReviewForm(request.POST, instance=review)
        if review_form.is_valid():
            review_form.save()
            return redirect("shop:detail", slug=review.product.slug)
    else:
        review_form = ReviewForm(instance=review)

    context = {
        "review_form": review_form,
        "review": review,
    }
    return render(request, "shop/edit_review.html", context)
