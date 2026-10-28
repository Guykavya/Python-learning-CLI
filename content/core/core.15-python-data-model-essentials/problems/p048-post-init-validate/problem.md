# Validate and derive fields in `__post_init__`

The generated `__init__` of a dataclass assigns the fields and then calls `self.__post_init__()` if
you defined it. That is the place for **validation**, **cleaning**, and **derived fields**.

- `field(init=False)`: not a parameter of `__init__`; you set it yourself (or give it a
  `default_factory`).
- `InitVar[...]`: a parameter of `__init__` that is **not** stored as a field. It is passed to
  `__post_init__` as an argument.
- In a **frozen** dataclass you cannot assign to fields, so `__post_init__` can only check them.

Write three dataclasses in `solution.py`.

**`Account`**: `owner: str`, `balance: float = 0.0`, and `history: list`, not an `__init__`
parameter, a new empty list per object. In `__post_init__`:

- the owner must be a `str` that is not blank, otherwise `ValueError`; a negative balance raises
  `ValueError` too;
- set `owner` to `owner.strip().title()`;
- append `("open", balance)` to `history`.

**`Range`** (frozen): `low: int`, `high: int`, `step: int = 1`. `__post_init__` raises `ValueError`
if `step <= 0` or `low > high`. The method `values()` returns `list(range(low, high + 1, step))`.

**`Rectangle`**: `width: float`, `height: float`, `unit_scale: InitVar[float] = 1.0`, and
`area: float` with `init=False`. `__post_init__(self, unit_scale)` multiplies **both** sides by
`unit_scale` and then sets `area = width * height`. `unit_scale` is not stored on the object.

**Example**

```python
Account("  asha rao ", 10.0)     # Account(owner='Asha Rao', balance=10.0, history=[('open', 10.0)])
Range(1, 10, 3).values()         # [1, 4, 7, 10]
Range(5, 1)                      # ValueError
Rectangle(2, 3, unit_scale=10)   # Rectangle(width=20.0, height=30.0, area=600.0)
```
