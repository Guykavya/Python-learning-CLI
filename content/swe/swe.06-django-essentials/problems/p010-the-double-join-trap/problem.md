# The double-join trap

Chapter section 7.5. The item list should show, for each item, **how many suppliers** can deliver it and **how many stock movements** it has had. Both numbers sit in other tables, so you use `annotate(Count(...))`. There is a trap: when one query counts across **two** relations, SQL joins both and the rows multiply.

In `solution.py` the models are written for you (do not change them): `Item` has a many-to-many `suppliers` (to `Supplier`) and a reverse foreign key `movements` (from `Movement`, one row per change of stock).

Write `item_stats()`. It returns a **QuerySet of `Item`** objects, ordered by name (the default), each with two extra attributes:

- `supplier_count`: the number of suppliers of the item,
- `movement_count`: the number of movements of the item,

both **correct** (an item with 2 suppliers and 3 movements has `2` and `3`, not `6` and `6`), `0` when there are none, computed in **one** query.

Think first: with a `LEFT JOIN` to suppliers *and* a `LEFT JOIN` to movements, an item with 2 suppliers and 3 movements becomes 2 x 3 = 6 rows. `Count("suppliers")` and `Count("movements")` each count those 6 rows. The tests are built so that the naive version is wrong. There are two ways to fix it (see the hints): `Count(..., distinct=True)`, or a `Subquery` for each number.

The tests set Django up for you (in-memory SQLite, your `solution.py` is the app `shop`, tables are created for your models); every model needs `class Meta: app_label = "shop"`; do not change a model while tests run.

## Example

```text
Item "Cable":   suppliers A, B      movements +50, -2, -1       -> supplier_count 2, movement_count 3
Item "Hub":     supplier A          no movements                -> 1, 0
Item "Mouse":   no suppliers        movements +10, +5           -> 0, 2
```

The starter uses plain `Count("suppliers")` and `Count("movements")`: for "Cable" it says `6` and `6`.
