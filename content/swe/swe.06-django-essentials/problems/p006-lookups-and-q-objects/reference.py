from django.db import models
from django.db.models import Q


class Category(models.Model):
    name = models.CharField(max_length=60, unique=True)

    class Meta:
        app_label = "shop"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Item(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        DISCONTINUED = "discontinued", "Discontinued"

    name = models.CharField(max_length=100, unique=True)
    sku = models.CharField(max_length=20, unique=True)
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="items")
    status = models.CharField(max_length=20, choices=Status, default=Status.ACTIVE)

    class Meta:
        app_label = "shop"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.sku})"


def search(text=None, max_price=None, in_stock=None):
    qs = Item.objects.exclude(status=Item.Status.DISCONTINUED)
    if text:
        qs = qs.filter(Q(name__icontains=text) | Q(sku__iexact=text))
    if max_price is not None:
        qs = qs.filter(price__lte=max_price)
    if in_stock is True:
        qs = qs.filter(quantity__gt=0)
    elif in_stock is False:
        qs = qs.filter(quantity=0)
    return qs
