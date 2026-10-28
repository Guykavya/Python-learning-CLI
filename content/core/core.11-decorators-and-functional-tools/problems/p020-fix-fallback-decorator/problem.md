# Fix: the @fallback decorator

**This code has bugs. Find them and fix them.**

A shop reads prices typed by staff, like `"Rs 12.50"`. Bad text such as `"free"` should not crash the
program; it should give `0.0`. A teammate wrote a decorator for this:

- `fallback(default)` is a decorator factory. If the decorated function raises `ValueError`, the wrapper
  returns `default` instead. Any other error must still reach the caller.
- If the function works, its result is returned unchanged.
- The decorated function must keep its own `__name__` and `__doc__`, because the shop's error report prints them.
- `parse_price(text)` uses it with a default of `0.0`.

The code in `starter.py` has **three** bugs. The teammate says: "Every price comes out as something weird,
and the report says the function is called `wrapper`."

1. Run the tests and read the first failing message.
2. For each bug, say in one sentence what is wrong before you change it.
3. Fix them. Keep the names `fallback` and `parse_price` and what they do.

**Example (after the fix)**

```python
parse_price("Rs 12.50")    # 12.5
parse_price(" 99 ")        # 99.0
parse_price("free")        # 0.0
parse_price.__name__       # 'parse_price'

@fallback(-1)
def to_int(text):
    return int(text)

to_int("42")    # 42
to_int("x")     # -1
```
