## Approach

Build the QuerySet step by step: start with the rule that always applies, then add one filter per argument that was given.

```python
def search(text=None, max_price=None, in_stock=None):
    qs = Item.objects.exclude(status=Item.Status.DISCONTINUED)
    if text:
        qs = qs.filter(Q(name__icontains=text) | Q(sku__iexact=text))
    if max_price is not None:
        qs = qs.filter(price__lte=max_price)
    if in_stock is True:
        qs = qs.filter(quantity__gt=0)
    elif in_stock is False:
        qs = qs.filter(quantity=0)
    return qs
```

- `exclude()` and `filter()` return new QuerySets; nothing runs in the database until the caller loops, counts or slices the result. That is why the function costs 0 queries and the caller can add `.filter(...)`, `.order_by(...)` or a slice.
- `Q(...) | Q(...)` is an OR inside one `filter()`. Two separate `filter()` calls are an AND.
- `text` uses `if text:` because `None` and `""` both mean "nothing typed". The other two use `is not None` / `is True` / `is False`, because `0` and `False` are legitimate values.
- `icontains` becomes `LIKE '%usb%'` (case-insensitive); `iexact` is a whole-value comparison. Searching the SKU with `iexact` is a design choice: SKUs are codes, and part of a code rarely means something.

## Complexity

Building the QuerySet is O(1). The SQL it produces is one `SELECT ... WHERE ...`; `LIKE '%x%'` cannot use an ordinary index, so on a big table it scans all rows (a real project would think about full-text search).

## Another way

Collect the conditions in a `Q()` object and apply them once: `q = Q(); if text: q &= Q(...) | Q(...)`; `return Item.objects.exclude(...).filter(q)`. An empty `Q()` means "no condition". Or build a dictionary of keyword filters, `{"price__lte": max_price}`, and pass it with `filter(**filters)`; that is neat for AND-only filters but cannot express the OR.
