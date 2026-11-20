# Lookups and `Q` objects

Chapter sections 6.4 and 6.6. The inventory page has a search box with three optional filters. In `solution.py` the models `Category` and `Item` are already written for you (do not change them). Write the function `search(text=None, max_price=None, in_stock=None)`.

It returns a **QuerySet** of `Item` objects (not a list), built with these rules, in any order of calls:

1. **Always** leave out discontinued items (`status="discontinued"`), even with no arguments.
2. `text`: keep items whose **name contains** the text (ignoring case) **or** whose **SKU equals** the text (ignoring case). That is `Q(name__icontains=text) | Q(sku__iexact=text)`. `None` or `""` means "no text filter".
3. `max_price`: keep items with `price <= max_price`. `None` means no filter. Careful: `0` is a real value ("free items only"), it is not "no filter".
4. `in_stock`: `True` keeps `quantity > 0`, `False` keeps `quantity == 0`, `None` means no filter. Careful: `False` is a real value too.
5. The default order of `Item` (by name) stays.

Because it is a QuerySet, calling `search()` runs **no** SQL; the query runs when the caller uses the result, and the caller may chain more filters on it.

The tests set Django up for you (in-memory SQLite, your `solution.py` is the app `shop`, tables are created for your models); every model needs `class Meta: app_label = "shop"`; do not change a model while tests run.

## Example

With items `USB cable (qty 120, 3.50)`, `USB hub (qty 0, 21.00)`, `Keyboard KB-1 (10, 49.90)` and a discontinued `USB dock`:

```text
search()                                 -> Keyboard, USB cable, USB hub
search(text="usb")                       -> USB cable, USB hub        (the dock is discontinued)
search(text="kb-1")                      -> Keyboard                  (SKU, any case)
search(text="usb", in_stock=True)        -> USB cable
search(max_price=21)                     -> USB cable, USB hub
```
