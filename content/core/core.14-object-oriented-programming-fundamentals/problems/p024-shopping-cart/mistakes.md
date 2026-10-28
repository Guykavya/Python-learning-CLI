- Writing `items = {}` in the class body instead of `self._lines = {}` in `__init__`. Then every
  cart shares one dict, and a product added to one visitor's cart appears in everybody's cart.
- Changing the cart first and checking later. A `ValueError` in the middle then leaves the cart
  half-changed.
- Leaving a product in the cart with qty 0 after `remove`. `items()` then shows a line nobody wants.
- Returning the number of products from `count()` instead of the number of pieces.
- Forgetting to round. `0.1 * 3` is `0.30000000000000004` in floating point.
- Using `if not price:` to check the price. It lets negative prices through.
- Checking only `qty < 1`. `1.5` pieces or the string `"2"` must be rejected too: use `isinstance(qty, int)`.
