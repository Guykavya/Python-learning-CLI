# Annotate a whole module

`starter.py` is a working inventory module with no hints. Copy it to `solution.py` and annotate
**every** function, so that `python -m mypy --strict solution.py` would pass. The tests check
every hint, and also that the functions still work.

The stock is a dict from item name to quantity: `{"apple": 5, "pear": 2}`. Read each body to see
what it takes and returns.

| Function | What it does |
|---|---|
| `add_stock(stock, item, qty)` | adds `qty` to an item (creating it if needed); returns nothing |
| `remove_stock(stock, item, qty)` | removes `qty` if there is enough and returns `True`; otherwise changes nothing and returns `False` |
| `quantity(stock, item)` | quantity of the item, `0` if unknown |
| `low_items(stock, threshold)` | sorted names of items with quantity below `threshold` |
| `price_total(stock, prices)` | sum of quantity times price for items that have a price (`prices` is a dict from name to decimal price) |
| `most_stocked(stock)` | the name with the highest quantity, or `None` for an empty stock |
| `apply_to_all(stock, func)` | a **new** dict with `func` applied to every quantity |
| `split_by_threshold(stock, threshold)` | a pair: the sorted names below the threshold, and the sorted names at or above it |

Hints to think about: which functions return nothing? Which can return `None`? Which parameter is
a function?
