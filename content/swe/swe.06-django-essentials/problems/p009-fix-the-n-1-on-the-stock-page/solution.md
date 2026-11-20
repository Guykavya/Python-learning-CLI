## Approach

```python
def stock_page(request):
    rows = []
    items = Item.objects.select_related("category").prefetch_related("tags")
    for item in items:
        rows.append({
            "name": item.name,
            "category": item.category.name,
            "tags": [tag.name for tag in item.tags.all()],
        })
    return JsonResponse({"count": len(rows), "items": rows})
```

- Before: `item.category` runs a query the first time you touch it (lazy loading) and so does `item.tags.all()`. With N items that is `1 + N + N` queries: the **N+1 problem**.
- `select_related("category")` follows the forward foreign key with a SQL `JOIN`: the item and its category arrive in **one** query.
- `prefetch_related("tags")` cannot use a single join (an item has many tags), so it runs a second query, `... WHERE item_id IN (...)`, and attaches the tags to the right items in Python. Total: **2 queries**, whether there are 4 items or 40,000.
- The tags come out sorted because `Tag.Meta.ordering = ["name"]` is used by the prefetch query. If you wrote `item.tags.order_by("name")` inside the loop, Django would ignore the prefetched data and run one query per item again.
- The test `test_the_number_of_queries_does_not_grow` is the real proof: a fix is a fix only if the count does not depend on N.

## Complexity

Queries: before `2N + 1`, after `2`. The JOIN query returns N rows; the prefetch query returns one row per (item, tag) pair.

## Another way

`Prefetch("tags", queryset=Tag.objects.order_by("name"))` makes the ordering of the prefetch explicit and lets you filter it (for example only tags that are visible). Or skip model objects: `Item.objects.values("name", "category__name")` is one query for the scalar columns, but then the tags still need their own query. For a list screen that shows only a few columns, `.only("name", "category__name")` with `select_related` loads even less data.
