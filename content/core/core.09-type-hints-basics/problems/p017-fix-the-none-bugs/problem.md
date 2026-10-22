# Fix the functions mypy would flag

`starter.py` is a small price-list module. It has hints, but **each of the last three functions
has a bug** that crashes or misbehaves at run time. For two of them mypy would report it; the
third is a crash that mypy cannot see. Copy
`starter.py` to `solution.py` and repair it.

```python
def find_price(menu: dict[str, float], item: str) -> float | None:   # correct, do not change
    return menu.get(item)
```

What the functions must do:

1. `total_cost(menu, order)` returns the sum of the prices of the items in `order`. Items that are
   **not on the menu are skipped** (they cost nothing). The return hint stays `float`.
2. `cheapest_item(menu)` returns the name of the item with the lowest price (the first one found
   if there is a tie), or `None` if the menu is empty. **Fix the hint as well as the code**:
   the function can return `None`, so `-> str` is a lie.
3. `price_label(menu, item)` returns `"$"` followed by the price with two decimals, for example
   `"$2.50"`, or `"n/a"` if the item is not on the menu.

Run the starter against the tests first and read what fails. The tests check the hints and the
behaviour.

**Examples**

```python
menu = {"tea": 2.5, "cake": 4.0}
total_cost(menu, ["tea", "cake", "soup"])   # 6.5   (soup is skipped)
cheapest_item(menu)                         # "tea"
cheapest_item({})                           # None
price_label(menu, "tea")                    # "$2.50"
price_label(menu, "soup")                   # "n/a"
```
