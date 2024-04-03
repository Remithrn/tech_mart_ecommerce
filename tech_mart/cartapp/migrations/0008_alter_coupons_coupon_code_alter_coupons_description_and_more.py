# Generated by Django 5.0.1 on 2024-03-25 05:47

import django.core.validators
import shop.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cartapp', '0007_alter_cart_coupon_alter_usercoupons_coupon_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupons',
            name='coupon_code',
            field=models.CharField(max_length=100, unique=True, validators=[django.core.validators.MinLengthValidator(5, 'Coupon code must be at least 5 characters'), shop.models.validate_non_empty]),
        ),
        migrations.AlterField(
            model_name='coupons',
            name='description',
            field=models.TextField(validators=[django.core.validators.MinLengthValidator(5, 'Description must be at least 5 characters'), shop.models.validate_non_empty]),
        ),
        migrations.AlterField(
            model_name='coupons',
            name='discount',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AlterField(
            model_name='coupons',
            name='minimum_amount',
            field=models.IntegerField(default=100),
        ),
    ]