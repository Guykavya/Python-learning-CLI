from django.db import models
from django.http import JsonResponse
from django.urls import path


class Category(models.Model):
    name = models.CharField(max_length=60, unique=True)

    class Meta:
        app_label = "shop"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)

    class Meta:
        app_label = "shop"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.CharField(max_length=100, unique=True)
    sku = models.CharField(max_length=20, unique=True)
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="items")
    tags = models.ManyToManyField(Tag, related_name="items", blank=True)

    class Meta:
        app_label = "shop"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.sku})"


def stock_page(request):
    rows = []
    items = Item.objects.select_related("category").prefetch_related("tags")
    for item in items:
        rows.append({
            "name": item.name,
            "category": item.category.name,
            "tags": [tag.name for tag in item.tags.all()],
        })
    return JsonResponse({"count": len(rows), "items": rows})


urlpatterns = [path("stock/", stock_page)]
