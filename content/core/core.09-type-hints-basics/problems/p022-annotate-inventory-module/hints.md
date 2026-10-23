## Hint 1

Do the easy ones first: `stock` is always `dict[str, int]`, `item` is `str`, `qty` and `threshold` are `int`. Then decide each return type from the **last line** of the body.

## Hint 2

`add_stock` has no `return`: that is `-> None`. `remove_stock` returns `True` or `False`. `most_stocked` has a `return None` branch. `apply_to_all` takes a function from `int` to `int`: you need `Callable` from `collections.abc`. `split_by_threshold` returns two lists in a fixed pair.

## Hint 3

```
add_stock(stock: dict[str, int], item: str, qty: int) -> None
remove_stock(stock: dict[str, int], item: str, qty: int) -> bool
quantity(stock: dict[str, int], item: str) -> int
low_items(stock: dict[str, int], threshold: int) -> list[str]
price_total(stock: dict[str, int], prices: dict[str, float]) -> float
most_stocked(stock: dict[str, int]) -> str | None
apply_to_all(stock: dict[str, int], func: Callable[[int], int]) -> dict[str, int]
split_by_threshold(stock: dict[str, int], threshold: int) -> tuple[list[str], list[str]]
```
