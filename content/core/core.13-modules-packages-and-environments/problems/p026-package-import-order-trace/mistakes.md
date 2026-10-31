- Printing `main: start` after the package lines. `main.py` prints before its first import.
- Printing `cart: done` before `models: start`. `cart` stops at `from . import models` until `models`
  has run to the end.
- Writing `models: got add`. When `models` runs, `cart` has not reached `def add` yet.
- Thinking `from . import cart` fails too. Since Python 3.7 it finds the half-built module in
  `sys.modules`; only importing a *name* that does not exist yet fails.
- Writing `cart: models has price? False`. By the time `cart` continues, `models` is finished.
- Forgetting that `shop.add` and `cart.add` are the same function, so the total counts three items.
- Thinking `cfg.TAX = 0` changes `cart.TAX`. `from .config import TAX` copied the value 10.
- In command 2, starting with `config: loading as __main__`. The package (and with it `shop.config`)
  is imported first; `config.py` runs twice.
- Copying the `RuntimeWarning` line. It goes to stderr, not to the printed output.
