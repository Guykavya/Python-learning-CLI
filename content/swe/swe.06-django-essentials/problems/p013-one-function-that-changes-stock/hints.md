## Hint 1

Two writes must succeed together: the new stock number and the `Movement` row. Which Django tool makes "all or nothing" for a block of code? And who should refuse a negative stock: an `if` in your function, or the database?

## Hint 2

Put both writes in `with transaction.atomic():`. For the stock, `Item.objects.filter(pk=item.pk).update(quantity=F("quantity") + delta)` lets SQLite compute the new value, so it also works when your `item` object is stale. The `CheckConstraint` makes that line raise `IntegrityError` when the result would be negative; the atomic block then rolls back everything done inside it. After the block, `item.refresh_from_db(fields=["quantity"])`.

## Hint 3

```text
Meta.constraints = [CheckConstraint(condition=Q(quantity__gte=0), name="item_quantity_not_negative")]

move_stock(item, delta, reason, user=None):
    if delta == 0: raise ValueError
    with transaction.atomic():
        movement = Movement.objects.create(item=item, delta=delta, reason=reason, user=user)
        Item.objects.filter(pk=item.pk).update(quantity=F("quantity") + delta)   # may raise IntegrityError
    item.refresh_from_db(fields=["quantity"])
    return movement
```
