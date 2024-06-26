# Generated by Django 5.0.1 on 2024-03-18 06:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0011_order_total_discount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('Razorpay', 'Razorpay'), ('Cash On Delivery', 'Cash On Delivery'), ('UPI', 'UPI')], default='Cash On Delivery', max_length=100),
        ),
    ]
