# Generated by Django 5.0.1 on 2024-03-16 06:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0010_alter_order_options_alter_order_customer'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='total_discount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=100),
        ),
    ]
