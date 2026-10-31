- Writing `return Product(...)` inside `from_row`. It works for `Product`, but a subclass like
  `Book.from_row(...)` then returns a plain `Product`. Use `cls(...)`.
- Converting in `__init__` (`self.price = float(price)`). Then `Product("X", "x", "10")` is
  accepted, and the class has two jobs. Keep string parsing in the alternative constructor.
- Making `Inventory` a subclass of `dict` or of `Product`. An inventory *has* products; it is not a
  product.
- Subtracting the stock before checking it. A failed sale then leaves a negative stock.
- Writing `stock <= threshold` in `low_stock`. "Below" means `<`.
- Sorting the result of `low_stock`. The problem asks for the order the products were added.
- Forgetting `.strip()`: `" P1"` and `"P1"` are different keys.
