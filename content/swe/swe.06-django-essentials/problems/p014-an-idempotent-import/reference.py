from django.db import models, transaction


class Item(models.Model):
    sku = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.IntegerField(default=0)

    class Meta:
        app_label = "shop"


def import_items(rows):
    by_sku = {row["sku"]: row for row in rows}          # last row of a sku wins
    with transaction.atomic():
        existing = set(Item.objects.filter(sku__in=list(by_sku)).values_list("sku", flat=True))
        new_items = [Item(sku=r["sku"], name=r["name"], price=r["price"])
                     for sku, r in by_sku.items() if sku not in existing]
        Item.objects.bulk_create(new_items)
        for sku in existing:
            row = by_sku[sku]
            Item.objects.filter(sku=sku).update(name=row["name"], price=row["price"])
    return len(new_items), len(existing)


urlpatterns = []
