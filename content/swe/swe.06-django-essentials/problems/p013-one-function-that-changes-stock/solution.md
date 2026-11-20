## Approach

```python
from django.conf import settings
from django.db import models, transaction
from django.db.models import F


class Item(models.Model):
    name = models.CharField(max_length=50)
    quantity = models.IntegerField(default=0)

    class Meta:
        app_label = "shop"
        constraints = [
            models.CheckConstraint(condition=models.Q(quantity__gte=0), name="item_quantity_not_negative"),
        ]


class Movement(models.Model):
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    delta = models.IntegerField()
    reason = models.CharField(max_length=20)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "shop"


def move_stock(item, delta, reason, user=None):
    if delta == 0:
        raise ValueError("delta must not be 0")
    with transaction.atomic():
        movement = Movement.objects.create(item=item, delta=delta, reason=reason, user=user)
        Item.objects.filter(pk=item.pk).update(quantity=F("quantity") + delta)
    item.refresh_from_db(fields=["quantity"])
    return movement
```

- **The database is the referee.** The `CheckConstraint` refuses any row with `quantity < 0`, whoever writes it: this function, the admin, a script. The function has no `if item.quantity + delta < 0`, because that check is a race: two requests can both read 10 and both subtract 8.
- **`F("quantity") + delta`** becomes `UPDATE ... SET quantity = quantity + 5` in SQL. The number in your Python object is never used, so a stale copy cannot overwrite a newer value.
- **`transaction.atomic()`** wraps both writes. When the `UPDATE` raises `IntegrityError`, the `Movement` created one line earlier is rolled back too. When `move_stock` itself runs inside another `atomic()` (like the tests), the inner block is a savepoint, so only its own work is undone.
- The `IntegrityError` leaves the `with` block, so the caller sees it and can show "not enough stock". Catch it **outside** the atomic block, never inside, or the transaction stays broken on PostgreSQL.
- `refresh_from_db(fields=["quantity"])` copies the new number into the object you were given.

## Complexity

Three SQL statements (insert, update, select for the refresh) plus the savepoint lines. O(1) in the size of the table.

## Another way

On PostgreSQL you would often use `select_for_update()` inside `atomic()`, read the row, check in Python and save. That gives a friendlier error message but needs row locks, which SQLite does not have. `F()` plus a constraint works on every database, and the constraint stays as the last line of defence even if somebody forgets the function.
