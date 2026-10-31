## Approach

**Command 1.** `main.py` runs as `__main__`. `import shop` runs `shop/__init__.py`:

1. `shop: start`.
2. `from . import config` runs `config.py` as `shop.config`: `config: loading as shop.config`.
   The `if` block is skipped because the name is not `__main__`.
3. `from .cart import add, total` starts `cart.py`: `cart: start`. `from .config import TAX` copies
   the value 10 (config is cached, nothing prints). `from . import models` starts `models.py`.
4. `models: start`. `from . import cart` finds the half-built `shop.cart` in `sys.modules`, which is
   allowed. `from .cart import add` fails, because `cart` stopped at its `from . import models` line
   and has not defined `add` yet: `models: no add yet`. Then `hasattr(cart, "add")` is `False`
   for the same reason. `models: done`.
5. Back in `cart`: `models` is finished, so it has `price`: `cart: models has price? True`.
   `cart: done`.
6. Back in `__init__`: `add` and `total` now exist. `shop: done, name = shop`.

`from shop import cart, models` and `import shop.config as cfg` only read the cache. Three items:
20 + 150 + 20 = 190, tax `190 * 10 // 100 = 19`, total 209. `shop.add` is the same function as
`cart.add`, so all three items go into one list. All three names point to one `cart` module object.
`cfg.TAX = 0` changes only `shop.config.TAX`; `cart.TAX` is its own copy and stays 10, so the total is
still 209.

**Command 2.** `-m shop.config` first imports the package `shop`, which prints the same six import
lines as before (`shop: start` ... `shop: done, name = shop`), including `config` as `shop.config`.
Then `config.py` runs a **second time**, now as `__main__`: `config: loading as __main__`, and this
time the `if` block runs. (This double run is what the `RuntimeWarning` on stderr warns about.)

## Output

```text
main: start, name = __main__
shop: start
config: loading as shop.config
cart: start
models: start
models: no add yet
models: cart has add? False
models: done
cart: models has price? True
cart: done
shop: done, name = shop
total: 209
same cart? True True
TAX now: 0 10
total after TAX = 0: 209
shop: start
config: loading as shop.config
cart: start
models: start
models: no add yet
models: cart has add? False
models: done
cart: models has price? True
cart: done
shop: done, name = shop
config: loading as __main__
config: run directly, TAX = 10
```

## Complexity

Not applicable.

## Another way

Fix the cycle so nothing depends on a half-built module. Either `models` never imports `cart` (it does
not need it: `PRICES` and `price` stand alone), or the import moves inside the function that needs it.
And read `TAX` as `config.TAX` at call time (`from . import config`) if it may change.
