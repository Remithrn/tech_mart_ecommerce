from django import forms
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from .models import Customer,Address

# Customer registration form

class CustomerRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Customer
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "username",
            "is_verified",
        )
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username.strip()) < 4:
            raise forms.ValidationError("Username must have at least 4 characters.")
        return username

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = (
            "street_address",
            "city",
            "state",
            "zip_code",
           
        )
        widgets = {
            "street_address": forms.TextInput(),
            "city": forms.TextInput(),
            "state": forms.TextInput(),
            "zip_code": forms.TextInput(),
           
        }

class CuatomerEditForm(UserChangeForm):
    password = None
    class Meta:
        
        model = Customer
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "username",
           
        )
        widgets = {
            "email": forms.EmailInput(),
            "phone_number": forms.NumberInput(),
            "username": forms.TextInput(),
            "first_name": forms.TextInput(),
            "last_name": forms.TextInput(),
           
        }
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username.strip()) < 4:
            raise forms.ValidationError("Username must have at least 4 characters.")
        return username

class AddressSelectForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields=("address",)
        widgets = {
            "address": forms.Select(attrs={"class":"form-control "}),
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(AddressSelectForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['address'].queryset = Address.objects.filter(user=user)