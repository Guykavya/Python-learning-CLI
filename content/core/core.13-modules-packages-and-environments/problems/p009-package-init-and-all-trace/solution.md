## Approach

1. `import shop` runs `shop/__init__.py`: `init shop`. That file never imports `cart`, so the package
   has no attribute `cart` yet: `False`.
2. The second `import shop` is answered from `sys.modules`: no output.
3. `import shop.cart` runs `cart.py`: `load cart`. Its line `from . import prices` means "the module
   `prices` in my own package", so `prices.py` runs: `load prices`. Every loaded submodule is also set as
   an attribute of its parent, so now `shop.cart` and `shop.prices` both exist: `True True`.
4. `10 + 50 + 10 = 70`.
5. `from shop.cart import total` loads nothing new and binds the same function object: `True`.
6. Submodule names are full dotted names: `shop.cart shop.prices`.
7. `from shop import *` follows `__all__`, so `main` gets `open_shop` and `cart`: `open 50`.
8. `prices` is not in `__all__`, and `_secret` is not either, so neither name was copied into `main`:
   `False False`.

## Output

```text
init shop
False
load cart
load prices
True True
70
True
shop.cart shop.prices
open 50
False False
```

## Complexity

O(1).

## Another way

Delete the `__all__` line and predict the last line again. Without `__all__`, `import *` copies every name
in the package that does not start with `_`. By then `prices` is an attribute of `shop`, so it is copied:
the last line becomes `True False`.
