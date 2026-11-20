## Approach

```python
def category_values():
    value = Coalesce(
        Sum(F("items__quantity") * F("items__price")),
        0,
        output_field=DecimalField(max_digits=12, decimal_places=2),
    )
    return Category.objects.annotate(value=value).order_by("-value", "name")
```

Django turns this into one query like:

```sql
SELECT category.id, category.name,
       COALESCE(SUM(item.quantity * item.price), 0) AS value
FROM shop_category AS category
LEFT OUTER JOIN shop_item AS item ON item.category_id = category.id
GROUP BY category.id
ORDER BY value DESC, category.name ASC
```

- `annotate()` with an aggregate on a reverse relation groups by the category and uses a **LEFT JOIN**, so categories without items stay in the result with `NULL`.
- `Sum` over no rows is `NULL` (`None` in Python). `Coalesce(..., 0)` swaps it for `0`. The `output_field` tells Django the result type, since the expression mixes an integer column and a decimal column and a literal `0`.
- The multiplication happens **in the database**: the work is done once, and no Python loop with one query per category is needed (that would be the N+1 problem of section 7.4).
- The annotation is a normal column for the rest of the QuerySet: you can `order_by("-value")`, `filter(value__gt=500)`, or paginate.

## Complexity

One query. The database joins and groups: roughly O(items) work plus a sort of the categories.

## Another way

`Category.objects.annotate(value=Sum(...)).order_by(F("value").desc(nulls_last=True))` leaves `None` in the data and only sorts it last; the template must then handle `None`. Computing in Python (`sum(i.quantity * i.price for i in category.items.all())`) is fine for one category, but for a list of 50 categories it costs 51 queries unless you also use `prefetch_related("items")`.
