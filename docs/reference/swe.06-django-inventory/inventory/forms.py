from django import forms

from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "sku", "category", "price", "reorder_level"]      # no quantity: use movements

    def clean_sku(self):
        return self.cleaned_data["sku"].strip().upper()

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price <= 0:
            raise forms.ValidationError("Price must be above zero.")
        return price
