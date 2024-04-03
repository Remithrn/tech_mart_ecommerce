# Generated by Django 5.0.1 on 2024-03-25 05:01

import django.core.validators
import shop.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0008_alter_review_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='category_discount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=250, unique=True, validators=[django.core.validators.MinLengthValidator(2, 'Category name must be at least 2 characters'), shop.models.validate_non_empty]),
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True, null=True, validators=[django.core.validators.MinLengthValidator(10, 'Product description must be greater than 10 characters'), shop.models.validate_non_empty]),
        ),
        migrations.AlterField(
            model_name='product',
            name='discount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=250, unique=True, validators=[django.core.validators.MinLengthValidator(3, 'Product name must be greater than 3 characters'), shop.models.validate_non_empty]),
        ),
        migrations.AlterField(
            model_name='product',
            name='stock',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='review',
            name='message',
            field=models.TextField(validators=[django.core.validators.MinLengthValidator(10, 'Review must be at least 10 characters'), shop.models.validate_non_empty]),
        ),
    ]
