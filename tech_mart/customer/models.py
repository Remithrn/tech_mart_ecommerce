from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator,MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
# Created Customer 
def validate_non_empty(value):
    if value.strip() == '':
        raise ValidationError("This field cannot be empty.")
class Address(models.Model):
    user = models.ForeignKey(
        'Customer',
        on_delete=models.CASCADE,
        related_name='addresses',
        blank=True,
        null=True)
    street_address = models.CharField(max_length=255 ,validators=[MinLengthValidator(10, "Street address must be at least 10 characters"),validate_non_empty])
    city = models.CharField(max_length=100,validators=[MinLengthValidator(5, "City must be at least 5 characters"),validate_non_empty])
    state = models.CharField(max_length=100,validators=[MinLengthValidator(5, "State must be at least 5 characters"),validate_non_empty])
    zip_code = models.CharField(max_length=20,validators=[MinLengthValidator(5, "Zip code must be at least 5 characters"),validate_non_empty])
    default_address = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.street_address}, {self.city}, {self.state} {self.zip_code}"
    
   
    
class Customer(AbstractUser):
    phone_number=models.CharField(max_length=15)
    address=models.ForeignKey(Address, on_delete=models.SET_NULL, related_name='customers',blank=True,null=True)
    otp=models.CharField(max_length=100,null=True,blank=True)
    is_verified=models.BooleanField(default=False)


class Wallet(models.Model):
    balance=models.DecimalField(max_digits=100,decimal_places=2,default=0)
    customer=models.OneToOneField(Customer,on_delete=models.CASCADE,related_name='wallet')

    def __str__(self):
        return f"{self.customer.username}'s Wallet"
    