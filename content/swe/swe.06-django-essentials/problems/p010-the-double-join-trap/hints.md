## Hint 1

Write the SQL in your head for one item with 2 suppliers and 3 movements: two `LEFT JOIN`s. How many rows does that item produce before `COUNT` runs? What does `COUNT(supplier_id)` count in those rows, and why is the number too big? Which keyword makes SQL count each value only once (`COUNT(DISTINCT ...)`)?

## Hint 2

`Count("suppliers", distinct=True)` becomes `COUNT(DISTINCT supplier.id)`: it counts each supplier once, however many times the join repeated it. The same for `movements`. The other fix gives each number its own subquery that counts rows of **one** table filtered by the outer item (`OuterRef("pk")`), so no join multiplies anything.

## Hint 3

```text
Item.objects.annotate(
    supplier_count=Count("suppliers", distinct=True),
    movement_count=Count("movements", distinct=True),
)
```
