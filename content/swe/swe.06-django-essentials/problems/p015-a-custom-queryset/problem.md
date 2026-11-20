# A custom QuerySet

Chapter section 9.5. A filter you use in many places (`quantity < 5`, `active = True`) should have a name and live in one place. Put it on the model's **QuerySet**, then it can be chained with every other filter.

The tests set Django up for you (in-memory SQLite, your `solution.py` is the app `shop`, tables are created for your models). Every model needs `class Meta: app_label = "shop"`. Do not change a model while the tests run.

The starter has `Category` (`name`, `slug`) and `Item` (`name`, `quantity`, `active`, `category` with `related_name="items"`). Write `ItemQuerySet` (a subclass of `models.QuerySet`) with three methods and attach it to `Item` with `as_manager()`:

| Method | Returns the items that... |
|---|---|
| `low_stock(threshold)` | have `quantity` **below** `threshold` (strictly less) |
| `active()` | have `active=True` |
| `in_category(slug)` | belong to the category with that `slug` (an unknown slug gives an empty result, no error) |

Each method returns a **QuerySet**, so the calls can be chained in any order: `Item.objects.active().low_stock(5).in_category("pens")`. They must work on the manager (`Item.objects.low_stock(5)`), on a queryset (`Item.objects.filter(...).low_stock(5)`) and on a related manager (`category.items.low_stock(5)`). Building a chain must not touch the database; only reading the result does (one query).

## Example

```text
pen   qty 2  active   pens
ink   qty 9  active   pens
cap   qty 1  inactive hats

Item.objects.low_stock(5)                       -> pen, cap
Item.objects.active().low_stock(5)              -> pen
Item.objects.low_stock(5).in_category("hats")   -> cap
```
