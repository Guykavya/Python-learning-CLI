## Hint 1

Count the queries by hand for 3 items: one for the list, then what for each item? Which attribute access inside the loop hits the database, and which relation kinds are they (a forward `ForeignKey`, a many-to-many)? Does the loop run on `Item.objects.all()`, which knows nothing about those relations?

## Hint 2

`select_related("category")` adds a `JOIN` to the first query, so `item.category` is already there. `prefetch_related("tags")` runs one more query for all tags of all items and matches them in Python, so `item.tags.all()` costs nothing. Put both on the QuerySet you loop over. Keep `item.tags.all()` in the loop: any other call on `item.tags` (`filter`, `order_by`) builds a new query.

## Hint 3

```text
items = Item.objects.select_related("category").prefetch_related("tags")
for item in items:
    ... item.category.name ... [t.name for t in item.tags.all()]
# total: 1 JOIN query + 1 prefetch query = 2 queries
```
