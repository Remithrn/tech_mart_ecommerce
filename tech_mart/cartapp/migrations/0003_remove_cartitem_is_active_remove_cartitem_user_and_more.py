# Generated by Django 5.0.1 on 2024-02-18 12:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cartapp', '0002_cartitem_date_added'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartitem',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='cartitem',
            name='user',
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='cart',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cartapp.cart'),
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='date_added',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='quantity',
            field=models.IntegerField(default=0),
        ),
    ]
