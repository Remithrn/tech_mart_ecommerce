# Generated by Django 5.0.1 on 2024-04-03 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0011_alter_address_city_alter_address_state_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='referral_code',
            field=models.CharField(blank=True, max_length=10, null=True, unique=True),
        ),
    ]
