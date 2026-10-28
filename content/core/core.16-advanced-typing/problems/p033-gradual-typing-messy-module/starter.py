def parse_price(text):
    """'$12.50' or ' 12.5 ' -> 1250 (cents). Bad text -> None."""
    text = text.strip().lstrip("$")
    try:
        return round(float(text) * 100)
    except ValueError:
        return None


def format_price(cents, symbol="$"):
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}{symbol}{cents // 100}.{cents % 100:02d}"


class Order:
    def __init__(self, order_id, customer, items=None):
        self.order_id = order_id
        self.customer = customer
        self.items = list(items) if items else []  # (name, cents, qty)

    def add(self, name, cents, qty=1):
        self.items.append((name, cents, qty))
        return self

    def total(self):
        return sum(cents * qty for _, cents, qty in self.items)

    def is_empty(self):
        return not self.items


def find_order(orders, order_id):
    for order in orders:
        if order.order_id == order_id:
            return order


def totals_by_customer(orders):
    totals = {}
    for order in orders:
        totals[order.customer] = totals.get(order.customer, 0) + order.total()
    return totals


def apply_discount(cents, percent):
    return cents - cents * percent // 100


def top_customer(orders):
    totals = totals_by_customer(orders)
    if not totals:
        return None
    name = max(totals, key=lambda n: totals[n])
    return name, totals[name]


def summarise(orders, symbol="$"):
    lines = []
    for order in orders:
        lines.append(f"#{order.order_id} {order.customer}: {format_price(order.total(), symbol)}")
    return lines


def filter_orders(orders, predicate):
    return [order for order in orders if predicate(order)]
