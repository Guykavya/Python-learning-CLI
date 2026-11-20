## Hint 1

Split the rows in two groups: skus that are already in the database and skus that are not. How many queries do you need to find out which group each sku is in? Think about `sku__in=[...]`.

## Hint 2

First make a dict `by_sku = {row["sku"]: row for row in rows}`: a repeated sku keeps its **last** row, and you count each sku once. Then one query: `Item.objects.filter(sku__in=list(by_sku)).values_list("sku", flat=True)`. The new ones go into a single `bulk_create`; the existing ones are updated (a loop of `filter(sku=...).update(...)` or `update_or_create` is fine for them). Put everything inside one `transaction.atomic()`.

## Hint 3

```text
by_sku = {sku: row}                                  # last row wins
with transaction.atomic():
    existing = set(skus already in the database)
    new_items = [Item(...) for sku not in existing]
    Item.objects.bulk_create(new_items)
    for sku in existing: update name and price only
return len(new_items), len(existing)
```
