from django.db import models
from shop.models import Product
from customer.models import Customer
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import MinLengthValidator,MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from shop.models import validate_non_empty
def validate_valid_dates(value):
    if value.valid_from >= value.valid_to:
        raise ValidationError({'valid_from': ('Valid from date must be earlier than valid to date.')})

# Create your models here.
class Coupons(models.Model):
    coupon_code = models.CharField(max_length=100, unique=True, validators=[MinLengthValidator(5, "Coupon code must be at least 5 characters"),validate_non_empty],)
    description = models.TextField(validators = [MinLengthValidator(5, "Description must be at least 5 characters"),validate_non_empty])
    minimum_amount = models.IntegerField(default=100)
    discount = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    is_expired = models.BooleanField(default=False)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def clean(self):
        validate_valid_dates(self)

    def __str__(self):
        return self.coupon_code

    def is_valid(self):
        now = timezone.now()
        if self.valid_to != now:
            self.is_expired = True
            return self.is_expired
        else:
            return self.is_expired

    def is_used_by_user(self, user):
        redeemed_details = UserCoupons.objects.filter(
            coupon=self, user=user, is_used=True
        )
        return redeemed_details.exists()
    class Meta:
        ordering = ("-updated",)
        verbose_name = 'coupon'
        verbose_name_plural = 'coupons'

class UserCoupons(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    coupon = models.ForeignKey(
        Coupons, on_delete=models.CASCADE, related_name="redeemed_by"
    )

    is_used = models.BooleanField(default=False)

    def __str__(self):
        return self.coupon.coupon_code


class Wishlist(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


class Cart(models.Model):

    user = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="carts")
    date_added = models.DateField(auto_now_add=True)
    coupon = models.ForeignKey(
        Coupons,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default="",
        related_name="carts",
    )

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for cart_item in self.cart_items.all():
            total += cart_item.total()

        return round(total, 2)

    def get_total_discount(self):
        total = 0
        for cart_item in self.cart_items.all():
            if cart_item.product.price_after_discount():
                total += cart_item.product.price_after_discount()
                
        print(f"{total} discount")
        return round(total, 2)

    def coupon_is_valid(self):
        if not self.coupon:
            print("No coupon applied.")
            return False
    
        if self.get_subtotal() < self.coupon.minimum_amount:
            print("Coupon minimum amount requirement not met.")
            return False
    
        if self.coupon.is_expired:
            print("Coupon is expired.")
            return False
    
        if self.coupon.valid_to < timezone.now():
            print("Coupon validity period has ended.")
            return False
    
        print("Coupon is valid.")
        return True

    def total_after_coupon(self):
        if self.coupon_is_valid():
            return round(self.get_total() - self.get_total() * self.coupon.discount / 100,2)
        else:
            return self.get_total()

    def get_subtotal(self):
        subtotal = 0
        for cart_item in self.cart_items.all():
            subtotal += cart_item.sub_total()
        return subtotal

    def is_already_used(self):
        if self.coupon.is_used_by_user(self.user):
            return True
        else:
            return False


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, blank=True
    )
    quantity = models.IntegerField(default=0)
    date_added = models.DateTimeField(auto_now_add=True)

    def total(self):
        if self.product.discount or self.product.category.category_discount:
           
            total = self.product.price_after_discount() * self.quantity 
        
        else:
         
            total = self.product.price * self.quantity
        return round(total, 2)

    def check_quantity(self):
        if self.quantity > self.product.stock:
            return False
        return True

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

    def sub_total(self):
        return self.product.price * self.quantity
