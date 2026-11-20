from django.db import models
from django.db.models import DecimalField, F, Sum
from django.db.models.functions import Coalesce


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


def category_values():
    value = Coalesce(
        Sum(F("items__quantity") * F("items__price")),
        0,
        output_field=DecimalField(max_digits=12, decimal_places=2),
    )
    return Category.objects.annotate(value=value).order_by("-value", "name")
