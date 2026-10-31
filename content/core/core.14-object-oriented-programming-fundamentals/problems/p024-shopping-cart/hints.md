## Hint 1

What must one cart remember? For every product: its price and its qty. Which collection lets you
find a product by its name quickly **and** keeps the order products were added? Where do you
create it so that every cart gets its own one: in the class body, or in `__init__`?

## Hint 2

Check everything **before** you change anything. Then a bad call leaves the cart exactly as it was.
`isinstance(qty, int)` tells you if `qty` is a whole number. `isinstance(price, (int, float))`
accepts both kinds of numbers.

## Hint 3

```
__init__:  self._lines = {}            # name -> [price, qty]

add(name, price, qty):
    if price is not a number or price <= 0: raise ValueError
    if qty is not an int or qty < 1:        raise ValueError
    if name in self._lines:
        if stored price != price: raise ValueError
        stored qty += qty
    else:
        self._lines[name] = [price, qty]

remove(name, qty):
    if name not in self._lines: raise KeyError(name)
    if qty < 1 or qty > stored qty: raise ValueError
    stored qty -= qty
    if stored qty == 0: del self._lines[name]
```
