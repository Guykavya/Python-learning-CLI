## Approach

This is what a mypy report looks like in practice: three real bugs, each caused by forgetting that a value can be `None`. mypy catches the first two; the third it misses (see below).

- `total_cost`: `total += find_price(...)` adds a `float | None`. mypy reports `Unsupported operand types for + ("float" and "None")`, and at runtime an unknown item raises `TypeError`. Fix: store the price in a variable, skip it when `is None`.
- `cheapest_item`: `best_name` starts as `None`, so the function really can return `None` (empty menu). mypy reports `Incompatible return value type (got "str | None", expected "str")`. Here the **hint** was wrong, not the body: change the return hint to `str | None`.
- `price_label`: `format(price, ".2f")` crashes with `TypeError` for a missing item, but mypy stays silent, because the built-in `format` accepts any object. A checker cannot find every bug, so know the `None` rule yourself. Fix: return `"n/a"` when `price is None`.

The question to ask for each mypy error is the one from the chapter: is the hint wrong, or is the code wrong? Here the answer was "code" for two functions and "hint" for one.

## Code

```python
def find_price(menu: dict[str, float], item: str) -> float | None:
    return menu.get(item)


def total_cost(menu: dict[str, float], order: list[str]) -> float:
    total = 0.0
    for item in order:
        price = find_price(menu, item)
        if price is None:
            continue
        total += price
    return total


def cheapest_item(menu: dict[str, float]) -> str | None:
    best_name = None
    best_price = 0.0
    for name, price in menu.items():
        if best_name is None or price < best_price:
            best_name, best_price = name, price
    return best_name


def price_label(menu: dict[str, float], item: str) -> str:
    price = find_price(menu, item)
    if price is None:
        return "n/a"
    return "$" + format(price, ".2f")
```

## Complexity

`total_cost` O(len(order)), `cheapest_item` O(len(menu)), `price_label` O(1).

## Another way

`total_cost` can ignore `find_price` and use `menu.get(item, 0.0)`, since a default removes the `None`. `price_label` could use `if item not in menu:` instead, because `menu[item]` is a plain `float`. Both avoid the narrowing step, but only work because "missing" has an easy default here.
