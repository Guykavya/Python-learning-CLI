from collections.abc import Callable


def parse_price(text: str) -> int | None:
    """'$12.50' or ' 12.5 ' -> 1250 (cents). Bad text -> None."""
    text = text.strip().lstrip("$")
    try:
        return round(float(text) * 100)
    except ValueError:
        return None


def format_price(cents: int, symbol: str = "$") -> str:
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}{symbol}{cents // 100}.{cents % 100:02d}"


class Order:
    def __init__(
        self,
        order_id: int,
        customer: str,
        items: list[tuple[str, int, int]] | None = None,
    ) -> None:
        self.order_id = order_id
        self.customer = customer
        self.items: list[tuple[str, int, int]] = list(items) if items else []

    def add(self, name: str, cents: int, qty: int = 1) -> "Order":
        self.items.append((name, cents, qty))
        return self

    def total(self) -> int:
        return sum(cents * qty for _, cents, qty in self.items)

    def is_empty(self) -> bool:
        return not self.items


def find_order(orders: list[Order], order_id: int) -> Order | None:
    for order in orders:
        if order.order_id == order_id:
            return order
    return None


def totals_by_customer(orders: list[Order]) -> dict[str, int]:
    totals: dict[str, int] = {}
    for order in orders:
        totals[order.customer] = totals.get(order.customer, 0) + order.total()
    return totals


def apply_discount(cents: int, percent: int) -> int:
    return cents - cents * percent // 100


def top_customer(orders: list[Order]) -> tuple[str, int] | None:
    totals = totals_by_customer(orders)
    if not totals:
        return None
    name = max(totals, key=lambda n: totals[n])
    return name, totals[name]


def summarise(orders: list[Order], symbol: str = "$") -> list[str]:
    lines = []
    for order in orders:
        lines.append(f"#{order.order_id} {order.customer}: {format_price(order.total(), symbol)}")
    return lines


def filter_orders(orders: list[Order], predicate: Callable[[Order], bool]) -> list[Order]:
    return [order for order in orders if predicate(order)]
