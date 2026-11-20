import re

from django import forms
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        app_label = "shop"


class Item(models.Model):
    name = models.CharField(max_length=50)
    sku = models.CharField(max_length=20, unique=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        app_label = "shop"


SKU_PATTERN = re.compile(r"^[A-Z]{2,4}-\d{3,5}$")


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["name", "sku", "price", "category"]

    def clean_sku(self):
        sku = self.cleaned_data["sku"].strip().upper()
        if not SKU_PATTERN.match(sku):
            raise forms.ValidationError("A sku looks like AB-123: 2-4 letters, a hyphen, 3-5 digits.")
        return sku


urlpatterns = []
