# A circuit breaker

Chapter section 21.6. When a service is down, trying again and again wastes time and makes things worse. A **circuit breaker** stops calling after repeated failures, **fails fast**, and tries again after a pause. Write

```python
class CircuitOpen(Exception): ...

class CircuitBreaker:
    def __init__(self, threshold, cooldown, clock): ...
    state                       # property: "closed", "open" or "half-open"
    def call(self, fn, *args, **kwargs): ...
```

`clock()` returns the current time in seconds (the tests use a fake one). The three states:

- **closed**: normal. `call` runs `fn(*args, **kwargs)` and returns its result. If `fn` raises an exception, the exception is **counted and re-raised**. After `threshold` failures **in a row** the breaker becomes **open**. A success resets the count to 0.
- **open**: `call` does **not** run `fn` at all: it raises `CircuitOpen` at once. After `cooldown` seconds since it opened, the state becomes **half-open**.
- **half-open**: the next `call` is a **trial**: it runs `fn`. If it succeeds the breaker becomes **closed** (count 0). If it raises, the breaker becomes **open** again (the cooldown starts again from now) and the exception is re-raised.

`state` is computed from the clock: it shows `"half-open"` as soon as `cooldown` seconds have passed (`now - opened_at >= cooldown`), even before anybody calls.

## Example

```python
t = [0.0]
cb = CircuitBreaker(threshold=2, cooldown=10, clock=lambda: t[0])
# two failing calls -> cb.state == "open"
# at t=5: cb.call(f) raises CircuitOpen and f is not called
# at t=10: cb.state == "half-open"; a successful call closes it
```
