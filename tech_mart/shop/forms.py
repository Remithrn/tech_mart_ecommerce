import os
from django import forms
from .models import Product, Category, ProductImage, Brand, Review


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        exclude = ["slug", "created", "updated"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ["slug"]
        widgets = {
            "name": forms.TextInput(attrs={}),
            "brand": forms.Select(attrs={"class": "fs-poppins   w-100 p-2"}),
            "description": forms.Textarea(attrs={"class": "input-data textarea"}),
            "label": forms.Select(attrs={"class": "fs-poppins   w-100 p-2"}),
            "price": forms.NumberInput(attrs={}),
            "discount": forms.NumberInput(attrs={}),
            "category": forms.Select(attrs={"class": "fs-poppins  w-100 p-2"}),
            "stock": forms.NumberInput(attrs={}),
            "available": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_discount(self):
        discount = self.cleaned_data.get("discount")
        if discount > 100 or discount < 0:
            raise forms.ValidationError("Discount must be between 0 and 100")
        return discount


class ProductImageForm(forms.ModelForm):
    images = forms.FileField(
        widget=forms.TextInput(
            attrs={
                "name": "images",
                "type": "File",
                "class": "form-control",
                "multiple": "True",
            }
        ),
        label="",
        required=False,
    )

    def clean_images(self):
        files =  self.cleaned_data.getlist("images")
        images = self.cleaned_data.get("images")

        for image in images:
            # Check for valid image format using a reliable list of extensions
            valid_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', '.webp']
            extension = os.path.splitext(image.name)[1].lower()
            print(extension)
            if extension not in valid_extensions:
                raise forms.ValidationError("Only image files allowed.")

        return images

    class Meta:
        model = ProductImage
        fields = ["images"]


class ProductFilterForm(forms.Form):
    price_min = forms.DecimalField(
        required=False, widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    price_max = forms.DecimalField(
        required=False, widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.all(),
        required=False,
        widget=forms.Select(
            attrs={"class": "fs-poppins bg-black text-white rounded-pill w-100 p-2"}
        ),
    )

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=forms.Select(
            attrs={"class": "fs-poppins bg-black text-white rounded-pill w-100 p-2"}
        ),
    )


class ReviewForm(forms.ModelForm):

    class Meta:
        RATING_CHOICES = [
            (0, "0 Stars"),
            (1, "1 Star"),
            (2, "2 Stars"),
            (3, "3 Stars"),
            (4, "4 Stars"),
            (5, "5 Stars"),
        ]
        model = Review
        fields = ["rating", "message"]
        widgets = {
            "rating": forms.Select(choices=RATING_CHOICES),
            "message": forms.Textarea(
                attrs={
                    "class": "input-data textarea fs-poppins form-control border  w-100 p-3",
                },
            ),
        }
