## Approach

```python
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
```

- **Idempotent** means: same input, same final state, however often you run it. The natural key (`sku`, which is `unique=True`) decides "create or update", so a second run finds every sku and only rewrites the same values.
- **Why not `update_or_create` for every row?** It is correct and short (`Item.objects.update_or_create(sku=..., defaults={...})` returns `(obj, created)`), but it costs about two queries per row plus a savepoint. For 300 new rows that is 600+ queries. Here: one query to find the existing skus and one `bulk_create` (SQLite splits it into a few `INSERT`s because of its variable limit).
- **`defaults`/`update()` only name `name` and `price`.** `quantity` is not in the update, so it keeps its value. With `update_or_create(defaults={...,"quantity": 0})` you would reset the stock on every import: a very common bug.
- **`transaction.atomic()`** around everything gives all-or-nothing. A bad row in the middle of a night import should not leave half the catalogue changed.
- `bulk_create` does not call `save()` and sends no `post_save` signal (section 16.2); fine here.

## Complexity

Let n be the number of rows. One `IN` query, one batch insert, and one `UPDATE` per existing sku: O(n) statements in the worst case for a re-import, O(1) statements (a few batches) for a first import. For a huge re-import you could also use `bulk_update`.

## Another way

```python
created = updated = 0
with transaction.atomic():
    for row in by_sku.values():
        _, was_created = Item.objects.update_or_create(
            sku=row["sku"], defaults={"name": row["name"], "price": row["price"]})
        created += was_created
        updated += not was_created
```

Simplest and always right, but slow for big files. Use it when the file is small; use the bulk version when it is not.
