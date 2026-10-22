def find_price(menu: dict[str, float], item: str) -> float | None:
    return menu.get(item)


def total_cost(menu: dict[str, float], order: list[str]) -> float:
    total = 0.0
    for item in order:
        total += find_price(menu, item)
    return total


def cheapest_item(menu: dict[str, float]) -> str:
    best_name = None
    best_price = 0.0
    for name, price in menu.items():
        if best_name is None or price < best_price:
            best_name, best_price = name, price
    return best_name


def price_label(menu: dict[str, float], item: str) -> str:
    price = find_price(menu, item)
    return "$" + format(price, ".2f")
