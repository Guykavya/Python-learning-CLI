## Hint 1

`import shop` runs only `shop/__init__.py`. Does that file import `cart`? Then `import shop.cart` runs
`cart.py`, which itself imports `prices`. When a submodule is loaded, Python also sets it as an
**attribute** of its parent package. Which attributes does `shop` have after that?

## Hint 2

The second `import shop` and `from shop.cart import total` find everything in `sys.modules`, so nothing
prints. A submodule's `__name__` is its full dotted name. `from shop import *` copies exactly the names
in `__all__` (`open_shop` and `cart`) into `main`, nothing else.
