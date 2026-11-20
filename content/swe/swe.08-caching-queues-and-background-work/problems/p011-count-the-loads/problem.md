# Count the loads

Chapter section 6.1 (the stampede) and "Try it: count the loads". A popular key has just expired. Requests keep arriving at a steady rate, and each request that **misses** starts a database load that takes `load_ms`. With **single flight**, only the first missing request loads; the others wait for its result. This simulation counts the loads in one second:

```python
def count_loads(rate_per_s, load_ms, single_flight, duration_ms=1000):
    """Requests arrive every 1000/rate ms, starting at t=0, just after the key expired."""
    gap = 1000 / rate_per_s
    value_ready_at = None          # when the first finished load puts the value in the cache
    lock_until = None              # single flight: someone is loading until then
    loads = 0
    t = 0.0
    while t < duration_ms:
        if value_ready_at is not None and t >= value_ready_at:
            pass                                   # hit
        elif single_flight and lock_until is not None:
            pass                                   # wait for the one loader
        else:
            loads += 1                             # miss: start a load
            finish = t + load_ms
            if value_ready_at is None:
                value_ready_at = finish
            lock_until = finish
        t += gap
    return loads


print("1:", count_loads(200, 100, single_flight=False))
print("2:", count_loads(200, 100, single_flight=True))
print("3:", count_loads(50, 100, single_flight=False))
print("4:", count_loads(1000, 250, single_flight=False))
print("5:", count_loads(10, 50, single_flight=False))
print("6:", count_loads(400, 100, single_flight=False))
```

## What to write

The exact output: six lines. Work each one out by reasoning first ("how many requests arrive before the first load finishes?"), then check the boundary carefully: a request that arrives **exactly** when the value becomes ready is a hit (`t >= value_ready_at`).

## Example

Line 5: requests every 100 ms, a load takes 50 ms. The request at t=0 loads (ready at 50 ms); the next request arrives at 100 ms, a hit. So `5: 1`.

## After you answer

- Line 6 doubles the rate of line 1. What happened to the number of loads? Write the rule as a formula.
- In a real database, loads get **slower** when many run at once. How would that change line 1?
