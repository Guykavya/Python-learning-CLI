# Fix: add types to a messy module, keep the behaviour

`starter.py` is a small order-handling module that works but has **no type hints at all**. This is
what most real code looks like when a team decides to start using mypy. Copy it to `solution.py`
and add annotations everywhere, **without changing what any function does**. The tests check that
the behaviour is the same, and that the hints are right.

Read each body to find out what it takes and returns. An order has `items`: a list of
`(name, price_in_cents, quantity)` tuples. Prices are whole numbers of cents.

| Function / method | Required hints |
|---|---|
| `parse_price(text)` | `text: str` -> `int \| None` (it returns `None` for bad text) |
| `format_price(cents, symbol="$")` | `cents: int`, `symbol: str = "$"` -> `str` |
| `Order.__init__(self, order_id, customer, items=None)` | `order_id: int`, `customer: str`, `items: list[tuple[str, int, int]] \| None = None` -> `None` |
| `Order.add(self, name, cents, qty=1)` | `name: str`, `cents: int`, `qty: int = 1` -> `Order` (or `Self`) |
| `Order.total(self)` | -> `int` |
| `Order.is_empty(self)` | -> `bool` |
| `find_order(orders, order_id)` | `orders: list[Order]`, `order_id: int` -> `Order \| None` |
| `totals_by_customer(orders)` | `orders: list[Order]` -> `dict[str, int]` |
| `apply_discount(cents, percent)` | `cents: int`, `percent: int` -> `int` |
| `top_customer(orders)` | `orders: list[Order]` -> `tuple[str, int] \| None` |
| `summarise(orders, symbol="$")` | `orders: list[Order]`, `symbol: str = "$"` -> `list[str]` |
| `filter_orders(orders, predicate)` | `orders: list[Order]`, `predicate: Callable[[Order], bool]` -> `list[Order]` |

Where the table says `list[Order]` for a parameter, `Sequence[Order]` and `Iterable[Order]` are
also accepted (a wider parameter type is allowed). Return types must match exactly.

Rules:

- Every function and method (including `__init__`) must have a hint for **every** parameter
  (except `self`) and for the return. The tests check this with `inspect.signature`.
- No `Any` anywhere in the hints.
- One function can quietly return `None` when something is not found. Find it, and make the
  hint say so.
- Do not change behaviour. `python -m mypy --strict solution.py` should pass.

**Example**

```python
parse_price("$12.50")           # 1250
parse_price("abc")              # None
Order(1, "Asha").add("pen", 150, 2).total()   # 300
find_order([], 7)               # None
```

**Remember**: the aim of gradual typing is to add safety **without** breaking working code. After
adding hints, the first thing to check is that the old behaviour tests still pass.
