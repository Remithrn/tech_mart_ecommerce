from django import forms
from .models import Coupons
class CouponApplyForm(forms.Form):
    code = forms.CharField(label='Coupon Code')

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupons
        fields = ['coupon_code', 'description','minimum_amount', 'discount', 'is_expired', 'valid_from', 'valid_to']
        widgets = {
          
            
            'valid_from': forms.DateTimeInput(attrs={'class': 'form-control','type':'datetime-local'},),
            'valid_to': forms.DateTimeInput(attrs={'class': 'form-control','type':'datetime-local'},),
        }