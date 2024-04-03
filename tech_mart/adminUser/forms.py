from customer.models import Customer
from django.contrib.auth.forms import UserCreationForm
from django import forms
from orders.models import Order, OrderItem

class AdminCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Customer
        fields = (
            "first_name",
            "last_name",
            "address",
            "email",
            "phone_number",
            "username",
            "is_superuser",
        )
    def save(self, commit=True):
        user = super().save(commit=False)

        if self.cleaned_data['is_superuser']:
            user.is_staff = True

        if commit:
            user.save()

        return user
    
class DeactivateCustomerForm(forms.Form):
    confirm_deactivation = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class OrdersForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer',  'total_price', 'payment_status', 'delivery_status', 'payment_method','complete','is_cancelled','delivery_address' ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize form fields as needed:
        self.fields['customer'].disabled = True
        self.fields['total_price'].disabled = True
        self.fields['payment_method'].disabled = True
        self.fields['is_cancelled'].disabled = True
        self.fields['delivery_address'].disabled = True
