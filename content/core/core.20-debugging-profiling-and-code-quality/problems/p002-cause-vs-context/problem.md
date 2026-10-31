# Trace: cause vs context

Every exception object carries three attributes that describe the chain behind it:

- `__context__`: the exception that was **being handled** when this one was raised (set
  automatically by Python).
- `__cause__`: the exception named in `raise ... from X` (set only by `from`).
- `__suppress_context__`: `True` after any `raise ... from ...` (including `from None`); it
  tells the traceback printer not to show the "During handling ..." part.

Those three decide whether a traceback says *"The above exception was the direct cause of the
following exception"*, *"During handling of the above exception, another exception occurred"*,
or nothing at all.

What does this program print?

```python
def show(label, exc):
    print(label, type(exc).__name__,
          type(exc.__cause__).__name__,
          type(exc.__context__).__name__,
          exc.__suppress_context__)


def explicit():
    try:
        int("x")
    except ValueError as e:
        raise KeyError("k") from e


def implicit():
    try:
        {}["a"]
    except KeyError:
        raise TypeError("t")


def hidden():
    try:
        1 / 0
    except ZeroDivisionError:
        raise ValueError("v") from None


def broken_handler():
    try:
        [][0]
    except IndexError:
        return totl


def plain():
    raise RuntimeError("r")


def reraise():
    try:
        raise OSError("o")
    except OSError:
        raise


def cause_only():
    raise LookupError("l") from AttributeError("a")


for func in [explicit, implicit, hidden, broken_handler, plain, reraise, cause_only]:
    try:
        func()
    except Exception as exc:
        show(func.__name__, exc)
```

Note: `type(None).__name__` is `'NoneType'`. In `broken_handler`, `totl` is a typo nobody
defined.

**Example**: the line for `plain` is `plain RuntimeError NoneType NoneType False`: nothing was
being handled and there is no `from`.

Write in `answer.txt` the seven lines the program prints, in order.
