# Trace: import order in a package with a circular import

This is the assessment trace of the module. It mixes everything: code that runs at import time,
a package `__init__.py`, relative imports, a circular import that **partly** works, a
`from`-import that copies a value, and `__name__` under `python -m`.

```text
project/
├── main.py
└── shop/
    ├── __init__.py
    ├── cart.py
    ├── config.py
    └── models.py
```

`shop/__init__.py`:

```python
print("shop: start")
from . import config
from .cart import add, total
print("shop: done, name =", __name__)
```

`shop/config.py`:

```python
print("config: loading as", __name__)
TAX = 10

if __name__ == "__main__":
    print("config: run directly, TAX =", TAX)
```

`shop/cart.py`:

```python
print("cart: start")
from .config import TAX
from . import models

print("cart: models has price?", hasattr(models, "price"))
_items = []


def add(item):
    _items.append(item)


def total():
    sub = sum(models.price(i) for i in _items)
    return sub + sub * TAX // 100


print("cart: done")
```

`shop/models.py`:

```python
print("models: start")
from . import cart

try:
    from .cart import add
    print("models: got add")
except ImportError:
    print("models: no add yet")

PRICES = {"pen": 20, "book": 150}


def price(item):
    return PRICES[item]


print("models: cart has add?", hasattr(cart, "add"))
print("models: done")
```

`main.py`:

```python
print("main: start, name =", __name__)
import shop
from shop import cart, models
import shop.config as cfg

cart.add("pen")
cart.add("book")
shop.add("pen")
print("total:", shop.total())
print("same cart?", shop.cart is cart, models.cart is cart)
cfg.TAX = 0
print("TAX now:", cfg.TAX, cart.TAX)
print("total after TAX = 0:", cart.total())
```

Kavya runs two commands from inside `project/`:

```bash
python main.py
python -m shop.config
```

In `answer.txt`, write everything the first command prints, then directly below it everything the
second command prints. One line per printed line, no blank line between the two runs.

Facts you need:

- Neither command stops with an error.
- The second command also writes a `RuntimeWarning` to **stderr**. It is not part of the printed
  output: leave it out.
- While a module is still running its top-level code, it is already in `sys.modules`. Another
  module that imports it gets the **half-built** module object. `from . import cart` succeeds with a
  half-built module (Python finds it in `sys.modules`). `from .cart import add` needs the name `add`
  to exist **already**, otherwise it raises `ImportError`.
- `python -m shop.config` imports the package `shop` first, then runs `shop/config.py` as `__main__`.

## Example of the format

`print("x:", True, 5 // 2)` prints `x: True 2`.
