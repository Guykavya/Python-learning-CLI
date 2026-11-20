# An idempotent import

Chapter sections 9.1 and 9.2. A supplier sends a list of products every night. Running the import twice (a retry, a double click) must give the same database as running it once. That property is called **idempotence**.

The tests set Django up for you (in-memory SQLite, your `solution.py` is the app `shop`, tables are created for your models). Every model needs `class Meta: app_label = "shop"`. Do not change a model while the tests run.

The starter has the model:

```python
class Item(models.Model):
    sku = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.IntegerField(default=0)
```

Write `import_items(rows)`. `rows` is a list of dicts with the keys `"sku"`, `"name"` and `"price"` (the price is a string such as `"2.50"`).

- A row whose `sku` is **not** in the database creates an `Item` (quantity 0).
- A row whose `sku` **is** in the database updates `name` and `price` of that item. `quantity` is never touched: it belongs to the stock-keeping code, not to the supplier.
- The function returns the tuple `(created, updated)`: how many items were created and how many existing ones were updated (an existing item counts as updated even when the values were the same).
- If the **same sku appears twice** in `rows`, the **last** row wins and the sku counts once.
- **All or nothing:** if any row fails (for example `price=None`), nothing from this call stays in the database.
- A big first import must not cost one query per row: for 300 new rows the tests allow at most 12 queries. (Hint: `bulk_create`.)

## Example

```text
rows = [{"sku": "A1", "name": "Pen", "price": "1.50"}, {"sku": "B2", "name": "Ink", "price": "4.00"}]
import_items(rows)   -> (2, 0)
import_items(rows)   -> (0, 2)      # second run: same database
```
