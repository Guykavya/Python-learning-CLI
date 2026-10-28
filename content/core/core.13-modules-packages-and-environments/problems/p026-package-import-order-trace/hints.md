## Hint 1

Follow the imports like a stack of open function calls. `main` imports `shop`, so `shop/__init__.py`
starts. Its second line imports `config` (finished at once). Its third line starts `cart`. `cart`
starts `models`. What does `models` find when it asks for `cart`: a finished module or a half-built one?
Which names does the half-built `cart` have at that moment?

## Hint 2

Draw the stack:

```text
main.py
  shop/__init__.py       prints "shop: start"
    config.py            prints "config: loading as shop.config", finishes
    cart.py              prints "cart: start", gets TAX = 10
      models.py          prints "models: start"
        from . import cart     -> half-built cart, fine
        from .cart import add  -> add is not defined yet -> ImportError
        ... models finishes
    back in cart: models is complete now -> has price? 
    cart finishes
  shop finishes
```

For the totals: 20 + 150 + 20, plus 10% with `//`. `cart.TAX` was copied by `from .config import TAX`.
Does changing `cfg.TAX` change `cart.TAX`?

For the second command: what does importing the package `shop` print, and under which name does
`config.py` run the first time? The second time?
