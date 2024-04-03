from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from customer.models import Customer
from django.core.validators import MinLengthValidator,MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

def validate_non_empty(value):
    if value.strip() == '':
        raise ValidationError("This field cannot be empty.")

class Category(models.Model):
    name = models.CharField(max_length=250, unique=True, validators=[MinLengthValidator(2, "Category name must be at least 2 characters"),validate_non_empty],)
    slug = models.SlugField(max_length=250, unique=True)
    image = models.ImageField(upload_to="category", blank=True)
    category_discount = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "category"
        verbose_name_plural = "categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=250, unique=True)
    image = models.ImageField(upload_to="brand", blank=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "brand"
        verbose_name_plural = "brands"

    def __str__(self):
        return self.name


class Product(models.Model):
    class Labels(models.TextChoices):
        NEW = "New", "New"
        Popular = "Popular", "Popular"
        Best_Seller = "Best Seller", "Best Seller"

    name = models.CharField(max_length=250, unique=True, validators=[MinLengthValidator(3, "Product name must be greater than 3 characters"),validate_non_empty],)
    label = models.CharField(max_length=11, choices=Labels.choices, default=Labels.NEW)
    slug = models.SlugField(max_length=250, unique=True)
    description = models.TextField(blank=True, null=True, validators=[MinLengthValidator(10, "Product description must be greater than 10 characters"),validate_non_empty])
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    stock = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated",)
        verbose_name = "product"
        verbose_name_plural = "products"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Product, self).save(*args, **kwargs)

    def price_after_discount(self):
        
        if self.discount > 0 and self.discount < 100:
            print("Discount product")
            return round(self.price - (self.price * self.discount / 100),2)
        elif self.category.category_discount > 0 and self.category.category_discount < 100:
            print("Discount category")
            return round(self.price - (self.price * self.category.category_discount / 100),2)
        else:
            print("No discount")
            return self.price
    
    


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.FileField(upload_to="product", blank=True, default="images/p-4.jpg")

    def __str__(self):
        return f"{self.product.name} - Image {self.id}"


Stars = [
    (0, "☆☆☆☆☆"),
    (1, "⭐☆☆☆☆"),
    (2, "⭐⭐☆☆☆"),
    (3, "⭐⭐⭐☆☆"),
    (4, "⭐⭐⭐⭐☆"),
    (5, "⭐⭐⭐⭐⭐"),
]


class Review(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="reviews"
    )
    message = models.TextField(validators=[MinLengthValidator(10, "Review must be at least 10 characters"),validate_non_empty])
    rating = models.IntegerField(choices=Stars, default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product.name} - Review {self.id}"

    def avg_rating(self):
        return Review.objects.filter(product=self.product, active=True).aggregate(
            models.Avg("rating")
        )["rating__avg"]
    class Meta:
        ordering = ("-updated",)
        verbose_name = "review"
        verbose_name_plural = "reviews"
    
    