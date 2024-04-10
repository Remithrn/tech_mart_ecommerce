"""
Order and OrderItem models for ecommerce site.

Order tracks order details like customer, status, payment info. 
OrderItem tracks line items with product and quantity.
"""

from django.db import models
from customer.models import Customer
from cartapp.models import Cart
from shop.models import validate_non_empty
from django.core.validators import MinLengthValidator,MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

# Create your models here.
class Order(models.Model):
    PAYMENT_CHOICES = (
        ("Razorpay", "Razorpay"),
        ("Cash On Delivery", "Cash On Delivery"),
        ("Wallet", "Wallet"),
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE,related_name='orders')
    payment_status = models.CharField(
        max_length=20,
        choices=[("Pending", "Pending"), ("Paid", "Paid"),("Failed","Failed")],
        default="Pending",
    )
    delivery_status = models.CharField(
        max_length=20,
        choices=[
            ("Pending", "Pending"),
            ("Shipped", "Shipped"),
            ("Delivered", "Delivered"),
            ("Cancelled", "Cancelled"),
        ],
        default="Pending",
    )
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True)
    payment_method = models.CharField(
        max_length=100, choices=PAYMENT_CHOICES, default="Cash On Delivery"
    )
    delivery_address = models.CharField(max_length=250, null=True,validators=[MinLengthValidator(10, "Delivery address must be at least 10 characters"),validate_non_empty])
    is_cancelled = models.BooleanField(default=False)
    total_price = models.DecimalField(max_digits=100, decimal_places=2, default=0)
    total_discount = models.DecimalField(max_digits=100, decimal_places=2, default=0)
    razorpay_payment_id = models.CharField(max_length=100, null=True,blank = True)
    razorpay_order_id = models.CharField(max_length=100, null=True,blank = True)
    razorpay_payment_signature = models.CharField(max_length=100, null=True,blank = True)
    is_returned = models.BooleanField(default=False)
    delivery_date = models.DateTimeField(null=True,blank = True)
    

    def __str__(self):
        return f"{self.customer.username}'s Order #{self.id}"
    class Meta:
        ordering = ['-date_ordered','is_cancelled']
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE,related_name='order_items')
    product = models.ForeignKey("shop.Product", on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=100, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

    def total_per_item(self):
        if self.product.discount:
            total = self.product.price * self.quantity - (
                self.product.price * self.quantity * self.product.discount / 100
            )
        else:
            total = self.product.price * self.quantity
        return round(total, 2)
    
