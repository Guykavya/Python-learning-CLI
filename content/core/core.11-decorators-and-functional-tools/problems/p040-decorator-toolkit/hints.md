## Hint 1

Write and test one decorator at a time, in this order: `logger`, `timer`, `retry`, `cache`,
`rate_limit`. All five have the same skeleton. Which parts of that skeleton run once per
factory call, once per decorated function, and once per call? Where does per-function state
(the cache dict, the list of call times) belong?

```
def name(settings...):
    check settings, raise ValueError         # once per factory call
    def decorator(func):
        state = ...                          # once per decorated function
        @wraps(func)
        def wrapper(*args, **kwargs):        # every call
            ...
        return wrapper
    return decorator
```

## Hint 2

- `timer`: `start = clock()`, then `try: return func(...)` and `finally: log.append(...)`.
- `retry`: keep a variable `wait = delay`. After each `sleep(wait)` do `wait = wait * backoff`.
  Use `if attempt == attempts: raise` inside the `except`.
- `logger`: like `timer`, but with `except Exception as err:` to record the class name
  (`type(err).__name__`), then `raise`.

## Hint 3

`cache`: store `key -> (value, stored_at)` in a dict.
On a call, if the key is there, `pop` it. If it is still fresh, put it back (now it is the
newest) and count a hit. Otherwise (missing or expired) count a miss, call the function, store
`(value, clock())`, and if the dict is bigger than `maxsize`, delete `next(iter(store))`.
Keep the counters in a small dict (or use `nonlocal`) so `cache_info` and `cache_clear` can see them.

## Hint 4

`rate_limit`: keep a list of the times of allowed calls. On every call:

```
now = clock()
keep only the times t with now - t < period
if len(times) >= calls:
    raise RuntimeError(f"rate limit exceeded for {name}: ... try again in {times[0] + period - now:.2f}s")
times.append(now)
return func(*args, **kwargs)
```

To change the list in place (so the closure keeps the same list), use `times[:] = [...]`.
