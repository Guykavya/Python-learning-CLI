## Hint 1

Do it function by function. For each one read the body and ask: what goes in (what does the code do with each parameter?) and what comes out (look at **every** `return`, including the end of the function)? Which function can reach the end without a `return`?

## Hint 2

Things that need a decision: `find_order` falls off the end, so it also returns `None`. `parse_price` returns `None` in the `except`. `Order.add` returns `self`. The attribute `self.items` is built from a list of tuples, so give it the same type as the constructor argument. Also add `return None` explicitly where the function can return nothing, so the intent is visible (it does not change behaviour).

## Hint 3

```
from collections.abc import Callable

parse_price(text: str) -> int | None
format_price(cents: int, symbol: str = "$") -> str
class Order:
    __init__(self, order_id: int, customer: str, items: list[tuple[str, int, int]] | None = None) -> None
        self.items: list[tuple[str, int, int]] = ...
    add(...) -> "Order"       total(...) -> int      is_empty(...) -> bool
find_order(orders: list[Order], order_id: int) -> Order | None
totals_by_customer(...) -> dict[str, int]      (annotate the empty dict: totals: dict[str, int] = {})
top_customer(...) -> tuple[str, int] | None
summarise(...) -> list[str]
filter_orders(orders: list[Order], predicate: Callable[[Order], bool]) -> list[Order]
```
