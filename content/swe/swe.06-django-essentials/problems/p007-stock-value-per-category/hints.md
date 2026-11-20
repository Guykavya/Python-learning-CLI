## Hint 1

You want one row per category, with a number that comes from many item rows. Which QuerySet method adds a computed value to each row? How do you reach the items of a category: which name did the `ForeignKey` give to the reverse side? And what does SQL's `SUM` give for a group with no rows?

## Hint 2

`F("items__quantity") * F("items__price")` is the value of one item, `Sum(...)` adds them per category. `Sum` of nothing is `None`: wrap it in `Coalesce(Sum(...), 0, output_field=DecimalField(...))`. Sorting is done with `.order_by("-value", "name")`; `-` means descending, and the second key breaks ties.

## Hint 3

```text
value = Coalesce(Sum(F("items__quantity") * F("items__price")), 0, output_field=DecimalField(max_digits=12, decimal_places=2))
return Category.objects.annotate(value=value).order_by("-value", "name")
```
