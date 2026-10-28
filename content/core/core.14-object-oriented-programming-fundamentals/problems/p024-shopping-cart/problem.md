# A shopping cart class

An online shop keeps a cart for every visitor. Each cart remembers which products are in it, the
price of each product and how many pieces of it the visitor wants. Write the class `Cart` in
`solution.py`.

`Cart()` takes no arguments and starts empty. It has these methods:

- `add(name, price, qty=1)` puts `qty` pieces of a product in the cart.
  - `price` must be a number greater than 0, otherwise raise `ValueError`.
  - `qty` must be an `int` that is 1 or more, otherwise raise `ValueError`.
  - If the product is already in the cart, add `qty` to the pieces it already has. The price must
    be the same as before; a different price raises `ValueError` (the cart is not changed).
- `remove(name, qty=1)` takes `qty` pieces out.
  - A product that is not in the cart raises `KeyError`.
  - `qty` smaller than 1, or bigger than the pieces in the cart, raises `ValueError`.
  - When the pieces reach 0, the product leaves the cart completely.
- `total()` returns the sum of `price * qty` over all products, rounded to 2 decimals with `round(x, 2)`.
- `count()` returns the number of **pieces** (not products) in the cart.
- `items()` returns a list of `(name, price, qty)` tuples, in the order the products were first added.

Every cart is separate: adding to one cart must never change another.

**Example**

```python
cart = Cart()
cart.add("pen", 10)
cart.add("notebook", 45.5, 2)
cart.add("pen", 10, 3)
cart.items()      # [('pen', 10, 4), ('notebook', 45.5, 2)]
cart.count()      # 6
cart.total()      # 131.0
cart.remove("notebook")
cart.total()      # 85.5
cart.remove("pen", 4)
cart.items()      # [('notebook', 45.5, 1)]
cart.remove("pen")        # KeyError: 'pen'
cart.add("ink", 0)        # ValueError
cart.add("notebook", 50)  # ValueError: the price of notebook is 45.5
```
