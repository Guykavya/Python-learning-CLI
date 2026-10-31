# Trace: `__cause__`, `__context__` and `from None`

When an exception is raised while another one is being handled, Python links them. Every exception
object has three attributes for this:

- `__cause__`: the exception given with `raise ... from X` (or `None`).
- `__context__`: the exception that was being handled when this one was raised (or `None`). Python
  sets it **automatically**, even when you use `from`.
- `__suppress_context__`: `True` when the traceback should **not** show the context. `raise ... from
  something` (including `from None`) sets it to `True`.

Read the code and write down exactly what it prints.

```python
class ConfigError(Exception):
    pass


def name_of(err):
    if err is None:
        return None
    return type(err).__name__


def show(label, err):
    print(label + ":", name_of(err), "-", err)
    print("  cause:", name_of(err.__cause__))
    print("  context:", name_of(err.__context__))
    print("  suppress:", err.__suppress_context__)


def a():
    try:
        int("x")
    except ValueError:
        raise ConfigError("bad number")


def b():
    try:
        {}["port"]
    except KeyError as e:
        raise ConfigError("missing port") from e


def c():
    try:
        [][0]
    except IndexError:
        raise ConfigError("empty list") from None


def d():
    raise ConfigError("direct") from OSError("disk")


def e():
    try:
        1 / 0
    except ZeroDivisionError:
        return totl


def f():
    try:
        int("y")
    except ValueError:
        pass
    raise ConfigError("after")


def g():
    try:
        b()
    except ConfigError as err:
        raise RuntimeError("wrapped") from err


for func in (a, b, c, d, e, f):
    try:
        func()
    except Exception as err:
        show(func.__name__, err)

try:
    g()
except Exception as err:
    chain = []
    current = err
    while current is not None:
        chain.append(name_of(current))
        current = current.__cause__
    print(" -> ".join(chain))
```

In `answer.txt`, write the printed output, one line per printed line. Keep the two spaces at the
start of the indented lines (the checker ignores spaces at the **end** of a line only).

Facts you need:

- `int("x")` raises `ValueError`, `{}["port"]` raises `KeyError`, `[][0]` raises `IndexError`,
  `1 / 0` raises `ZeroDivisionError`.
- Using a name that does not exist raises `NameError` with the message `name '<the name>' is not defined`.
- `print(label + ":", ..., "-", err)` prints the exception's message for `err`.

## Example of the format

```python
try:
    int("z")
except ValueError as err:
    print("x:", type(err).__name__, "-", err.__cause__)
```

prints `x: ValueError - None`.
