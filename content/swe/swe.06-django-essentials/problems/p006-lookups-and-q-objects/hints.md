## Hint 1

Start from `Item.objects.exclude(...)` and add one `if` per optional argument, re-assigning the QuerySet each time (`qs = qs.filter(...)`). Each `filter()` returns a **new** QuerySet and does not run SQL. Which values of `max_price` and `in_stock` mean "no filter"? Is that the same as "false-looking"?

## Hint 2

Keyword arguments inside one `filter()` are joined with AND. For "this OR that", wrap each condition in `Q(...)` and join them with `|`. The lookups: `name__icontains`, `sku__iexact`, `price__lte`, `quantity__gt`. Use `if max_price is not None:` and compare `in_stock` with `True` / `False` explicitly, because `0` and `False` are values you want to apply.

## Hint 3

```text
qs = Item.objects.exclude(status="discontinued")
if text:                    qs = qs.filter(Q(name__icontains=text) | Q(sku__iexact=text))
if max_price is not None:   qs = qs.filter(price__lte=max_price)
if in_stock is True:        qs = qs.filter(quantity__gt=0)
elif in_stock is False:     qs = qs.filter(quantity=0)
return qs
```
