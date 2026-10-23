from collections.abc import Callable


def add_stock(stock: dict[str, int], item: str, qty: int) -> None:
    stock[item] = stock.get(item, 0) + qty


def remove_stock(stock: dict[str, int], item: str, qty: int) -> bool:
    if stock.get(item, 0) < qty:
        return False
    stock[item] -= qty
    return True


def quantity(stock: dict[str, int], item: str) -> int:
    return stock.get(item, 0)


def low_items(stock: dict[str, int], threshold: int) -> list[str]:
    return sorted(name for name, qty in stock.items() if qty < threshold)


def price_total(stock: dict[str, int], prices: dict[str, float]) -> float:
    return sum(qty * prices[name] for name, qty in stock.items() if name in prices)


def most_stocked(stock: dict[str, int]) -> str | None:
    if not stock:
        return None
    return max(stock, key=lambda name: stock[name])


def apply_to_all(stock: dict[str, int], func: Callable[[int], int]) -> dict[str, int]:
    return {name: func(qty) for name, qty in stock.items()}


def split_by_threshold(stock: dict[str, int], threshold: int) -> tuple[list[str], list[str]]:
    low = low_items(stock, threshold)
    ok = sorted(name for name in stock if name not in low)
    return low, ok
