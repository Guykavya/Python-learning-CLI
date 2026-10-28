# debug: a decorator that works with or without parentheses

Some decorators can be used in two ways:

```python
@debug
def add(a, b): ...

@debug(prefix="TRACE", log=lines)
def mul(a, b): ...
```

In the first case Python calls `debug(add)`: the function arrives directly. In the second,
Python first calls `debug(prefix="TRACE", log=lines)`, which must **return a decorator**, and then
calls that decorator with `mul`. One function has to handle both.

Write `debug(func=None, *, prefix="DEBUG", log=None)` in `solution.py`. The `*` makes `prefix`
and `log` keyword-only.

- `debug(some_function)` returns the decorated function.
- `debug()` and `debug(prefix=..., log=...)` return a decorator.
- If `func` is given but is **not callable**, for example `@debug("TRACE")`, raise `TypeError`
  with a message that tells the user to write `prefix="..."`.
- The decorated function, on every call, records this line and returns the result:

  `"<prefix>: <name>(<arguments>) -> <repr of result>"`

  Arguments are written with `repr` and joined by `", "`; keyword arguments come after
  positional ones as `key=repr(value)`.
- Recording means: `log.append(line)` if `log` is a list, else `print(line)`.
- If the function raises, record `"<prefix>: <name>(<arguments>) raised <ExceptionName>"` and
  let the exception continue.
- Use `functools.wraps`.

**Example**

```python
@debug
def add(a, b):
    return a + b

add(2, 3)        # prints: DEBUG: add(2, 3) -> 5

lines = []

@debug(prefix="TRACE", log=lines)
def greet(name, punct="!"):
    return "hi " + name + punct

greet("ann", punct="?")
lines            # ["TRACE: greet('ann', punct='?') -> 'hi ann?'"]
```
