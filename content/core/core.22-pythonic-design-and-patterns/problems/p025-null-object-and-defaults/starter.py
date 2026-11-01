PRICES = {"pen": 2, "book": 12, "lamp": 30}


class DictCache:
    """A real cache. Keep this class as it is."""

    def __init__(self):
        self.data = {}

    def get_or_compute(self, key, compute):
        if key not in self.data:
            self.data[key] = compute()
        return self.data[key]


def _price(sku):
    return PRICES[sku]


def price_order_lines(orders, logger=None, cache=None):
    """orders: list of (sku, qty). Returns a list of (sku, qty, line_total).
    Unknown SKUs are skipped (and logged as an error)."""
    lines = []
    for sku, qty in orders:
        if sku not in PRICES:
            if logger is not None:
                logger.error(f"unknown sku {sku}")
            continue
        if cache is not None:
            price = cache.get_or_compute(sku, lambda: _price(sku))
        else:
            price = _price(sku)
        if logger is not None:
            logger.info(f"priced {sku} x{qty}")
        lines.append((sku, qty, price * qty))
    return lines


def order_total(orders, logger=None, cache=None):
    lines = price_order_lines(orders, logger, cache)
    total = sum(line for _, _, line in lines)
    if logger is not None:
        logger.info(f"total {total}")
    return total
