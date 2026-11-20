# Stock value per category

Chapter sections 6.5 and 7.5. The owner asks: "How much money is sitting in the warehouse, per category?" The **stock value** of an item is `quantity * price`; the value of a category is the sum over its items.

The models `Category` and `Item` are already in `solution.py` (do not change them). Write `category_values()`. It returns a **QuerySet of `Category` objects**, each with an extra attribute `value` (the stock value of its items), computed **in the database** in a single query:

1. Every category appears, **also categories without items**; their `value` is `0`, not `None`.
2. A category whose items all have quantity 0 also has value `0`.
3. Order: highest `value` first; categories with the same value in alphabetical order of `name`.
4. Iterating the result costs exactly **one** query (no loop in Python that asks the database for each category).

All items count, whatever their status.

Hints about the tools: `annotate(value=...)` adds a computed column to each row; `F("items__quantity")` follows the reverse relation `items`; `Sum(...)` adds up the values; `Coalesce(x, 0)` replaces `NULL` (what `Sum` gives for a group with no rows) by a default; when you mix integers and decimals Django may need `output_field=DecimalField()`.

The tests set Django up for you (in-memory SQLite, your `solution.py` is the app `shop`, tables are created for your models); every model needs `class Meta: app_label = "shop"`; do not change a model while tests run.

## Example

```text
Cables      USB cable 120 x 3.50 = 420.00,  Cable tie 10 x 1.25 = 12.50    -> value 432.50
Computers   Keyboard 10 x 49.90 = 499.00,  Monitor 3 x 189.00 = 567.00     -> value 1066.00
Spare       (no items)                                                      -> value 0

category_values() -> Computers 1066.00, Cables 432.50, Spare 0
```
