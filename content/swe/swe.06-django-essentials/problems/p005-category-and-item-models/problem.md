# Category and Item models

Chapter sections 6.2 and 7.1. A model is a table. In `solution.py` write the two models of the inventory app, with exactly these fields (names, types and options matter; the tests read them through `Model._meta`).

**`Category`**

| Field | Definition |
|---|---|
| `name` | `CharField`, `max_length=60`, unique |

`str(category)` is the name. Default ordering: by `name`.

**`Item`**

| Field | Definition |
|---|---|
| `name` | `CharField`, `max_length=100`, unique |
| `sku` | `CharField`, `max_length=20`, unique |
| `quantity` | `PositiveIntegerField`, default `0` |
| `price` | `DecimalField`, `max_digits=8`, `decimal_places=2` (money is never a float) |
| `category` | `ForeignKey` to `Category`, `on_delete=PROTECT`, `related_name="items"` |
| `status` | `CharField`, `max_length=20`, `choices` from an inner class `Status(models.TextChoices)` with `ACTIVE = "active", "Active"` and `DISCONTINUED = "discontinued", "Discontinued"`; default `Status.ACTIVE` |

`str(item)` is `"<name> (<sku>)"`, for example `"USB cable (CB-1)"`. Default ordering: by `name`.

**Setup notes.** The tests set Django up for you (in-memory SQLite, your `solution.py` is the app `shop`, tables are created for your models); every model needs `class Meta: app_label = "shop"`; do not change a model while tests run. Put `ordering` into the same `Meta` class.

## Example

```python
cables = Category.objects.create(name="Cables")
item = Item.objects.create(name="USB cable", sku="CB-1", price="3.50", category=cables)
str(item)         # 'USB cable (CB-1)'
item.quantity     # 0
item.status       # 'active'
cables.items.count()   # 1: related_name="items"
cables.delete()   # raises ProtectedError: the category still has items
```
