from django import forms
from .models import Order,OrderItem

class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = Order
        type=[('Paypal','Paypal'),('Cash On Delivery','Cash On Delivery')]
        fields = ['payment_method']
        widgets = { 'payment_method': forms.Select(choices=type,attrs={"class":"form-control "}) }