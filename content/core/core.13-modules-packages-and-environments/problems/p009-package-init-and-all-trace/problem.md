# Trace: packages, submodules and `__all__`

A package is a folder with an `__init__.py`. Trace when each file runs, which names appear on the package,
and what `from shop import *` brings in.

```text
demo/
├── main.py
└── shop/
    ├── __init__.py
    ├── cart.py
    └── prices.py
```

`shop/__init__.py`:

```python
print("init shop")
__all__ = ["open_shop", "cart"]


def open_shop():
    return "open"


def _secret():
    return "hidden"
```

`shop/cart.py`:

```python
print("load cart")
from . import prices


def total(items):
    return sum(prices.PRICES[i] for i in items)
```

`shop/prices.py`:

```python
print("load prices")
PRICES = {"pen": 10, "book": 50}
```

`main.py`:

```python
import shop
print(hasattr(shop, "cart"))
import shop
import shop.cart
print(hasattr(shop, "cart"), hasattr(shop, "prices"))
print(shop.cart.total(["pen", "book", "pen"]))
from shop.cart import total
print(total is shop.cart.total)
print(shop.cart.__name__, shop.prices.__name__)
from shop import *
print(open_shop(), cart.total(["book"]))
print("prices" in dir(), "_secret" in dir())
```

You run `python main.py` inside `demo/`. Write exactly what it prints, one line for each printed line,
in `answer.txt`. The program never stops with an error.
