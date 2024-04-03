# Generated by Django 5.0.1 on 2024-02-18 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_remove_order_cart'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('Paypal', 'Paypal'), ('Cash On Delivery', 'Cash On Delivery')], default='Cash On Delivery', max_length=100),
        ),
    ]
