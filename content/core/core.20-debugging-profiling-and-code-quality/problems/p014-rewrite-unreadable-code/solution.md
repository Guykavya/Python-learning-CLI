## Approach

Rewriting code you do not understand is how new bugs are born. So the order is:

1. **Read and translate** each line into a sentence (see Hint 1).
2. **Pin down the behaviour** with *characterisation tests*: run the original on odd inputs and
   record what it does, whether or not it is "right". The test file does exactly that: it keeps
   the original and compares on a list of tricky inputs.
3. **Rewrite** with names, a docstring and a narrow `except`, then run the comparison again.

The quirks a careless rewrite changes:

| Quirk | Why it happens |
|---|---|
| `" #x,1,2"` is **not** a comment | `x[0] == '#'` looks at the first character only |
| `"pen, 2 ,3.5"` counts | `int(" 2 ")` and `float(" 3.5 ")` ignore surrounding spaces |
| `"pen,2.0,3"` is skipped | `int("2.0")` raises `ValueError` |
| `"Pen"` and `" pen "` are one product | the name is stripped and lower-cased |
| rounding happens **once**, at the end | `round(v[1], 2)` is applied to the total |
| ties sorted by name, **after** rounding | the sort key uses the rounded revenue |

## Code

```python
def summarise_orders(rows: list[str]) -> list[tuple[str, int, float]]:
    """Total quantity and revenue per product from "name,quantity,unit_price" rows.

    Skips empty rows, rows starting with "#", rows without exactly three fields, rows whose
    quantity is not an int or price not a float, and rows with quantity <= 0. Names are
    stripped and lower-cased. Returns (name, quantity, revenue rounded to 2 places), highest
    revenue first, ties by name.
    """
    totals: dict[str, list] = {}  # name -> [quantity, revenue]
    for row in rows:
        if not row or row.startswith("#"):
            continue
        fields = row.split(",")
        if len(fields) != 3:
            continue
        name_text, qty_text, price_text = fields
        try:
            quantity = int(qty_text)
            price = float(price_text)
        except ValueError:
            continue
        if quantity <= 0:
            continue
        name = name_text.strip().lower()
        entry = totals.setdefault(name, [0, 0.0])
        entry[0] += quantity
        entry[1] += quantity * price

    summary = [(name, qty, round(revenue, 2)) for name, (qty, revenue) in totals.items()]
    summary.sort(key=lambda item: (-item[2], item[0]))
    return summary
```

`row.startswith("#")` is the same as `x[0] == '#'` after the empty check, and it cannot raise.

## Complexity

O(n) to read n rows, O(p log p) to sort p products.

## Another way

Two dictionaries (`quantity_by_name`, `revenue_by_name`) or a small `dataclass` instead of the
two-item list read even better. A `collections.defaultdict(lambda: [0, 0.0])` removes the
`setdefault`. Any shape is fine **as long as the comparison tests still pass**: that is the
whole point of writing them first.

Should the quirks be fixed? Maybe (`" #x"` probably should be a comment). But that is a
**separate**, deliberate change with its own test, made after the clean-up, never mixed into it.
