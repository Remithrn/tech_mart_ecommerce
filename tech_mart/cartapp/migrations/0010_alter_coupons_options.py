# Generated by Django 5.0.1 on 2024-04-03 09:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cartapp', '0009_alter_coupons_options_coupons_created_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='coupons',
            options={'ordering': ('-updated',), 'verbose_name': 'coupon', 'verbose_name_plural': 'coupons'},
        ),
    ]