**1. Why "call 2".** `calls` is one global variable. `global calls` makes every wrapper read and
change that same variable. `count` is applied twice, so there are two wrappers, but both point to
the one global number. `add` raises it to 1, `mul` to 2, `add` to 3.

**2. The right place.** A decorator has two moments. The body of `count` runs **once for each
function it decorates**, at decoration time. The body of `wrapper` runs on every call. So a
variable created inside `count` (outside `wrapper`) is new for each decorated function and is
kept alive by the wrapper's closure. That is exactly "one counter per function".

**3. Fixed version.**

```python
def count(func):
    calls = 0

    def wrapper(*args):
        nonlocal calls
        calls += 1
        print(f"{func.__name__} call {calls}")
        return func(*args)
    return wrapper
```

`nonlocal` tells Python that `calls` is the variable in `count`'s scope, not a new local one.
Another way is a function attribute: set `wrapper.calls = 0` before `return wrapper` and use
`wrapper.calls += 1` inside. That also lets other code read `add.calls`.

**4. Shared state on purpose.** Sometimes all functions *should* share: for example a rate
limit for one web API, where `get_user` and `get_orders` together may make only 10 calls per
second. Then make the sharing explicit: create the shared object once and pass it in,
for example `limit = make_limiter(10)` and `@rate_limited(limit)` on both functions. A reader
then sees that they share, instead of discovering it through a bug.
