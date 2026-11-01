- `books: list = []`: dataclasses raise `ValueError: mutable default`. Use `field(default_factory=list)`.
- Forgetting `frozen=True` and then wondering why books cannot be put in a set (`unhashable`).
- Writing your own `__eq__` or `__lt__`: it is more code, easy to get out of sync with the fields, and the
  test refuses it.
- Reordering the fields: `order=True` compares in declaration order, so the sort order changes.
- Validating in `describe()` or in the caller instead of `__post_init__`. Then a bad book can exist.
- Trying to set a field inside `__post_init__` of a frozen class (`self.year = int(year)`). Use
  `object.__setattr__(self, "year", ...)` if you must convert, but validating is enough here.
