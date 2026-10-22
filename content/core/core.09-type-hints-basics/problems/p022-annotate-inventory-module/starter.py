def add_stock(stock, item, qty):
    stock[item] = stock.get(item, 0) + qty


def remove_stock(stock, item, qty):
    if stock.get(item, 0) < qty:
        return False
    stock[item] -= qty
    return True


def quantity(stock, item):
    return stock.get(item, 0)


def low_items(stock, threshold):
    return sorted(name for name, qty in stock.items() if qty < threshold)


def price_total(stock, prices):
    return sum(qty * prices[name] for name, qty in stock.items() if name in prices)


def most_stocked(stock):
    if not stock:
        return None
    return max(stock, key=lambda name: stock[name])


def apply_to_all(stock, func):
    return {name: func(qty) for name, qty in stock.items()}


def split_by_threshold(stock, threshold):
    low = low_items(stock, threshold)
    ok = sorted(name for name in stock if name not in low)
    return low, ok
