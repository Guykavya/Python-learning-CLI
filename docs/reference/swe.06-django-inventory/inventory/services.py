from django.db import transaction
from django.db.models import F

from .models import Product, StockMovement


class InsufficientStock(Exception):
    def __init__(self, product, wanted, available):
        super().__init__(f"Cannot remove {wanted} of {product.sku}: only {available} in stock.")
        self.product, self.wanted, self.available = product, wanted, available


@transaction.atomic
def record_movement(product, delta, reason, *, user=None, note=""):
    """Change a product's stock and record why. All or nothing."""
    if delta == 0:
        raise ValueError("A movement of zero units is meaningless.")
    rows = Product.objects.filter(pk=product.pk)
    if delta < 0:
        rows = rows.filter(quantity__gte=-delta)          # refuse to go below zero, inside the UPDATE
    if rows.update(quantity=F("quantity") + delta) == 0:
        product.refresh_from_db(fields=["quantity"])
        raise InsufficientStock(product, -delta, product.quantity)
    product.refresh_from_db(fields=["quantity"])
    return StockMovement.objects.create(product=product, delta=delta, reason=reason, note=note, created_by=user)
