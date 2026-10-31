# A call-tracing decorator

When a bug hides somewhere in a chain of calls, it helps to see every call, its arguments and
what it returned, **without** adding prints to every function. A decorator can do that, and
because it logs at `DEBUG`, it can stay in the code and cost (almost) nothing when debugging is
off.

Write `trace_calls(logger)` in `solution.py`. It returns a decorator. A decorated function
`f` behaves exactly as before, and in addition logs at **DEBUG** level on `logger`:

1. before the call: `logger.debug("call %s(%s)", name, arg_text)`
2. after it returns: `logger.debug("%s -> %r", name, result)`
3. if it raises: `logger.debug("%s raised %r", name, exc)`, then the **same** exception is
   raised again.

- `name` is `f.__name__`.
- `arg_text` is the positional arguments as `repr`s, then the keyword arguments as
  `key=repr(value)` in the order given, all joined with `", "`. No arguments gives `""`.
- Keep `f`'s metadata: `__name__`, `__doc__` and `__wrapped__` (use `functools.wraps`).
- **Cheap when off:** if `logger.isEnabledFor(logging.DEBUG)` is false, call `f` directly and
  do not build `arg_text` or call `repr` on anything. (Building `arg_text` calls `repr` on every
  argument, which can be slow for big objects.)

**Example**

```python
import logging
logging.basicConfig(level=logging.DEBUG, format="%(message)s")
log = logging.getLogger("calc")

@trace_calls(log)
def area(w, h, unit="m"):
    """Area of a rectangle."""
    return f"{w * h} {unit}2"

area(3, 4, unit="cm")
area.__name__, area.__doc__        # ('area', 'Area of a rectangle.')
```

```text
call area(3, 4, unit='cm')
area -> '12 cm2'
```

And when it raises:

```text
call parse_age('ten')
parse_age raised ValueError("invalid literal for int() with base 10: 'ten'")
```
