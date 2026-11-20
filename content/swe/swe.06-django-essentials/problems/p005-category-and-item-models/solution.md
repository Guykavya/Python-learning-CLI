## Approach

```python
from django.db import models


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
```

- `unique=True` creates a `UNIQUE` column: the **database** refuses duplicates, not only your Python code.
- `PositiveIntegerField` adds `CHECK (quantity >= 0)` to the table, so a stock level can never be stored negative.
- `DecimalField` keeps exact decimals (`Decimal("3.50")`). A float would store `0.1 + 0.2` style errors.
- `on_delete=PROTECT` makes `category.delete()` raise `ProtectedError` while items point to it. The alternative `CASCADE` would silently delete all its items.
- `related_name="items"` names the reverse side: `category.items.all()`. Without it Django would call it `item_set`.
- The `Status` class stores the short value (`"active"`) in the column and gives the readable label to forms and the admin.
- `Meta.app_label = "shop"` is only needed because the tests (and the chapter's sandbox) have no real app folder; in a real project the app is known from where `models.py` lives.

## Complexity

Defining models costs nothing at run time; the cost is in the table: each `unique=True` field builds an index, so inserts are slightly slower and lookups by `sku` are fast.

## Another way

`status = models.CharField(max_length=20, choices=[("active", "Active"), ("discontinued", "Discontinued")], default="active")` works as well, but then the strings are repeated all over your code. The `TextChoices` class gives names (`Item.Status.ACTIVE`) that your editor can complete and that you can rename safely.
