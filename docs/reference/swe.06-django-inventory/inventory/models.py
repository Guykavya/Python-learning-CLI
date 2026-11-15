from django.conf import settings
from django.db import models
from django.db.models import F
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=60, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def low_stock(self):
        return self.filter(quantity__lte=F("reorder_level"))


class Product(models.Model):
    name = models.CharField(max_length=100)
    sku = models.CharField("SKU", max_length=20, unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=5)
    created = models.DateTimeField(auto_now_add=True)

    objects = ProductQuerySet.as_manager()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.sku})"

    def get_absolute_url(self):
        return reverse("inventory:product-detail", kwargs={"pk": self.pk})

    @property
    def is_low(self):
        return self.quantity <= self.reorder_level


class StockMovement(models.Model):
    class Reason(models.TextChoices):
        RECEIVE = "receive", "Goods received"
        SALE = "sale", "Sale"
        ADJUST = "adjust", "Stock-take adjustment"

    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="movements")
    delta = models.IntegerField(help_text="Positive adds stock, negative removes it.")
    reason = models.CharField(max_length=20, choices=Reason)
    note = models.CharField(max_length=200, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name="+")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created", "-id"]
        constraints = [
            models.CheckConstraint(condition=~models.Q(delta=0), name="movement_delta_not_zero"),
        ]

    def __str__(self):
        return f"{self.product.sku} {self.delta:+d} ({self.reason})"
