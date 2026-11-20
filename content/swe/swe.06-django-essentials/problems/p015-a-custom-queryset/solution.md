## Approach

```python
class ItemQuerySet(models.QuerySet):
    def low_stock(self, threshold):
        return self.filter(quantity__lt=threshold)

    def active(self):
        return self.filter(active=True)

    def in_category(self, slug):
        return self.filter(category__slug=slug)


class Item(models.Model):
    ...
    objects = ItemQuerySet.as_manager()
```

- **Methods on the QuerySet, not on the manager.** Every QuerySet method (`filter`, `exclude`, ...) returns a new `ItemQuerySet`, so your methods are available again on the result. That is what makes `active().low_stock(5).in_category("pens")` work in any order. Methods that live only on a `Manager` subclass vanish after the first `filter()`.
- **`as_manager()`** builds a manager class from the QuerySet and copies its public methods onto it, so `Item.objects.low_stock(5)` works too. Django also uses the default manager for related managers, which is why `category.items.low_stock(5)` works.
- **`self.filter(...)`** keeps everything already in the chain (`self` may be a filtered queryset) and adds one more condition; it returns a new object and does not run SQL. SQL runs only when you iterate, slice with a step, call `list()`, `len()`, `exists()` and so on.
- `quantity__lt` is "less than"; `quantity__lte` would include the threshold itself.
- `category__slug` makes Django join the category table; an unknown slug just matches no rows.

## Complexity

Building the chain is O(1) per call. Reading it is one SQL query with all conditions combined in one `WHERE` (and one join for the category).

## Another way

Write `class ItemManager(models.Manager)` with `def get_queryset(self)` and the methods on it. You then get `Item.objects.low_stock(5)`, but not `Item.objects.filter(...).low_stock(5)`, unless you also write a QuerySet. A custom QuerySet is usually the better single place. If you need a method only on the manager, use `ItemQuerySet.as_manager()` for the shared ones and `Manager.from_queryset(...)` when you want to add manager-only methods.
