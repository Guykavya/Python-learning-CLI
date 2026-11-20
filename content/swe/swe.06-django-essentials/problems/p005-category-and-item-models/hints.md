## Hint 1

Each class attribute that is a field becomes a column. For every row of the table in the problem, which field class do you need, and which options does the row name (`unique`, `default`, `max_length`, `on_delete`...)? Which option on the `ForeignKey` makes `category.items` work, and which one forbids deleting a category that still has items?

## Hint 2

`Status(models.TextChoices)` is a class inside `Item` with members `ACTIVE = "active", "Active"`. The `choices=` option takes the class itself, and `default=Status.ACTIVE`. The `Meta` class holds `app_label` and `ordering`. `__str__` returns a string built from the fields.

## Hint 3

```text
class Category: name CharField(60, unique) ; Meta(app_label, ordering=["name"]) ; __str__ -> name
class Item:
    class Status(TextChoices): ACTIVE, DISCONTINUED
    name CharField(100, unique) ; sku CharField(20, unique)
    quantity PositiveIntegerField(default=0) ; price DecimalField(8, 2)
    category ForeignKey(Category, PROTECT, related_name="items")
    status CharField(20, choices=Status, default=Status.ACTIVE)
    Meta(app_label, ordering) ; __str__ -> "name (sku)"
```
