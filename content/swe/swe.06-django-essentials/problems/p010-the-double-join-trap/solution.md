## Approach

```python
def item_stats():
    return Item.objects.annotate(
        supplier_count=Count("suppliers", distinct=True),
        movement_count=Count("movements", distinct=True),
    )
```

- Counting through two relations in the same `annotate()` makes Django join **both** tables to `item`. An item with 2 suppliers and 3 movements then gives `2 x 3 = 6` result rows, each carrying one supplier and one movement. `COUNT(supplier.id)` counts 6 non-null values, and so does `COUNT(movement.id)`.
- `distinct=True` produces `COUNT(DISTINCT supplier.id)`: the 6 rows contain only 2 different suppliers and 3 different movements, so you get `2` and `3`.
- For an item with no suppliers the `LEFT JOIN` gives `NULL`, and `COUNT` ignores `NULL`, so you get `0` with no `Coalesce` needed (that is different from `Sum`).
- Cost of the trap: it is not only wrong, it is also slow, because the intermediate result has `suppliers x movements` rows per item. `distinct=True` fixes the numbers, but the join is still built.

## Complexity

One query. With `distinct=True` the database still builds the multiplied rows (`suppliers x movements` per item) and then removes duplicates while counting. For 100 suppliers and 1,000 movements of one item that is 100,000 rows for that item alone.

## Another way

Count each relation in its own subquery, so nothing is multiplied:

```python
from django.db.models import IntegerField, OuterRef, Subquery
from django.db.models.functions import Coalesce

movements = (Movement.objects.filter(item=OuterRef("pk")).order_by()
             .values("item").annotate(n=Count("pk")).values("n"))
suppliers = (Item.suppliers.through.objects.filter(item_id=OuterRef("pk")).order_by()
             .values("item_id").annotate(n=Count("pk")).values("n"))
Item.objects.annotate(
    movement_count=Coalesce(Subquery(movements, output_field=IntegerField()), 0),
    supplier_count=Coalesce(Subquery(suppliers, output_field=IntegerField()), 0),
)
```

It is longer, but each count is a small independent query and it scales with `suppliers + movements`, not their product. Use it when the relations are big; use `distinct=True` when they are small.
