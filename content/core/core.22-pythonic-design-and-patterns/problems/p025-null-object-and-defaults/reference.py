PRICES = {"pen": 2, "book": 12, "lamp": 30}


class NullLogger:
    def info(self, message):
        pass

    def error(self, message):
        pass


class NullCache:
    def get_or_compute(self, key, compute):
        return compute()


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


def price_order_lines(orders, logger=NullLogger(), cache=NullCache()):
    lines = []
    for sku, qty in orders:
        if sku not in PRICES:
            logger.error(f"unknown sku {sku}")
            continue
        price = cache.get_or_compute(sku, lambda: _price(sku))
        logger.info(f"priced {sku} x{qty}")
        lines.append((sku, qty, price * qty))
    return lines


def order_total(orders, logger=NullLogger(), cache=NullCache()):
    lines = price_order_lines(orders, logger, cache)
    total = sum(line for _, _, line in lines)
    logger.info(f"total {total}")
    return total
