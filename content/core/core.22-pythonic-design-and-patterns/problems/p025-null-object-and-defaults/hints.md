## Hint 1

What does the code want to do when there is no logger? Nothing. What if "nothing" were
itself an object with the same methods as a real logger? Where could you put that object so
the caller never has to pass one?

## Hint 2

```
class NullLogger:  info(message) -> do nothing;  error(message) -> do nothing
class NullCache:   get_or_compute(key, compute) -> return compute()

def price_order_lines(orders, logger=NullLogger(), cache=NullCache()):
    ... logger.error(...)                      # always called
    ... cache.get_or_compute(sku, lambda: _price(sku))   # always called
```

Now delete every `if ... is not None` from both functions. Only the `sku not in PRICES` check
stays: it is real logic, not a None check.
