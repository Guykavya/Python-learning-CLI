# Compose functions

Write `compose(*funcs)` that returns a **new function** of one argument. Calling it applies the
functions from **right to left**, like mathematics: `compose(f, g, h)(x)` is `f(g(h(x)))`.

`compose()` with no functions returns a function that gives back its argument unchanged
(the "identity" function).

**Examples**

```python
def inc(n):
    return n + 1

def double(n):
    return n * 2

compose(inc, double)(5)        # inc(double(5)) = 11
compose(double, inc)(5)        # double(inc(5)) = 12
shout = compose(str.upper, str.strip)
shout("  hi  ")                # "HI"
compose()(42)                  # 42
```

`compose` itself must **not** call any of the functions; they run only when the returned
function is called.
