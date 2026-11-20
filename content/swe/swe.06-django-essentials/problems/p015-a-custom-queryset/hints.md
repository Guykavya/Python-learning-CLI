## Hint 1

Where must a method live so that it can be called on `Item.objects`, on `Item.objects.filter(...)` and on `category.items`? On the manager class, or on the QuerySet class? And what does a method have to return to be chainable?

## Hint 2

Put the three methods in `ItemQuerySet(models.QuerySet)`. Each one is `return self.filter(...)`. Strictly below is the lookup `quantity__lt`; the category lookup goes through the relation: `category__slug`. Then in `Item` write `objects = ItemQuerySet.as_manager()`; Django creates a manager with a copy of every public QuerySet method.

## Hint 3

```text
class ItemQuerySet(models.QuerySet):
    low_stock(self, threshold): return self.filter(quantity__lt=threshold)
    active(self):               return self.filter(active=True)
    in_category(self, slug):    return self.filter(category__slug=slug)

class Item: objects = ItemQuerySet.as_manager()
```
