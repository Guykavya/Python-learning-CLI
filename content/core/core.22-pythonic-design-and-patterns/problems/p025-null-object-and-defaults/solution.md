## Approach

Both optional parts have a natural "do nothing" version: a logger that ignores messages, and a
cache that never remembers (so it always computes). Give the functions those as defaults.
Every `if x is not None` disappears and the real logic (skip unknown SKUs, price, add up) is
what you read. The null objects follow the same interface as the real ones (*polymorphism*),
so the calling code does not know which it has.

## Code

```python
class NullLogger:
    def info(self, message):
        pass

    def error(self, message):
        pass


class NullCache:
    def get_or_compute(self, key, compute):
        return compute()


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
```

(`PRICES`, `_price` and `DictCache` stay as in the starter.)

## Complexity

Same as before: O(len(orders)). A null call costs one empty method call.

## Another way

Share the two objects as module constants (`_NO_LOG = NullLogger()`) and use them as the
defaults. The standard library does this: `logging.NullHandler` and `contextlib.nullcontext`
are null objects, and `unittest.mock` is full of them.

Null objects fit when "do nothing" is a sensible behavior. If a missing value is an
**error** (a database you cannot work without), failing loudly is better than hiding it.
Never make a null object that silently returns wrong data.
