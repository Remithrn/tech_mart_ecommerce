# Generated by Django 5.0.1 on 2024-03-26 04:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0017_alter_order_delivery_address'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ['-date_ordered', 'is_cancelled']},
        ),
    ]
