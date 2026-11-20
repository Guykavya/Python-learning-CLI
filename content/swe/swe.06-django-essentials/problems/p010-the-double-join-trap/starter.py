from django.db import models
from django.db.models import Count


class Category(models.Model):
    name = models.CharField(max_length=60, unique=True)

    class Meta:
        app_label = "shop"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=60, unique=True)

    class Meta:
        app_label = "shop"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.CharField(max_length=100, unique=True)
    sku = models.CharField(max_length=20, unique=True)
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="items")
    suppliers = models.ManyToManyField(Supplier, related_name="items", blank=True)

    class Meta:
        app_label = "shop"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.sku})"


class Movement(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="movements")
    delta = models.IntegerField()
    reason = models.CharField(max_length=60, blank=True)

    class Meta:
        app_label = "shop"


def item_stats():
    # TODO: this counts joined rows, not suppliers and movements
    return Item.objects.annotate(supplier_count=Count("suppliers"), movement_count=Count("movements"))
