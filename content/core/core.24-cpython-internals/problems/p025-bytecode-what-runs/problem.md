# Trace: what the code objects and frames say

A function carries a **code object** (`f.__code__`) that the compiler filled in before the
function ever ran, and every running call has a **frame** that remembers where it is and what
its variables hold. A generator keeps its frame alive between `next()` calls. This program asks
both of them questions. Predict every line it prints **without running it**.

The program only prints facts that are the same on Python 3.11, 3.12, 3.13 and 3.14. (That is
also why it never prints a `dis` listing, a refcount or `None in co_consts`: those change between
versions.)

Facts you may need (not the answer):

- `co_varnames` lists the parameters first, then the other local variables in the order the
  compiler first meets them. `co_names` lists global (and attribute) names the code uses.
- `co_consts` holds the literal values the bytecode needs. The compiler **folds** constant
  expressions such as `"ab" * 3` before it stores constants.
- A docstring is stored in the function's `co_consts`. A nested `def` is stored there as a
  **code object** (the function object itself is made only when `make_helper` runs).
- `sys._getframe(1)` is the frame of the caller; `f_lineno` is the line it is executing now.
- `inspect.getgeneratorstate(g)` returns `"GEN_CREATED"`, `"GEN_RUNNING"`, `"GEN_SUSPENDED"` or
  `"GEN_CLOSED"`. `g.gi_code.co_firstlineno` is the line of the `def`.
- `dict(...)` makes a new, independent dictionary.

```python
import inspect
import sys


def where():
    return sys._getframe(1).f_lineno


def measure(a, b=2):
    "Add with a twist."
    first = where()
    total = a + b
    label = "ab" * 3
    second = where()
    return second - first, total, label


def countdown(n):
    while n > 0:
        yield n
        n -= 1
    return "done"


def make_helper():
    def helper():
        return 1000
    return helper


def outer():
    return inner()


def inner():
    frame = sys._getframe()
    return [frame.f_code.co_name, frame.f_back.f_code.co_name, frame.f_back.f_back.f_code.co_name]


def snapshot_demo():
    x = 1
    snap = dict(sys._getframe().f_locals)
    x = 2
    return snap["x"], x


code = measure.__code__
print(code.co_name, code.co_argcount, code.co_varnames)
print("ababab" in code.co_consts, "ab" in code.co_consts, "Add with a twist." in code.co_consts)
print(code.co_names)
print(measure(5))

g = countdown(2)
print(inspect.getgeneratorstate(g), g.gi_frame is None)
print(next(g), inspect.getgeneratorstate(g))
print(g.gi_frame.f_locals["n"], g.gi_frame.f_lineno - g.gi_code.co_firstlineno)
print(next(g), g.gi_frame.f_locals["n"])
try:
    next(g)
except StopIteration as stop:
    print("stop", stop.value)
print(inspect.getgeneratorstate(g), g.gi_frame is None)
print(bool(countdown.__code__.co_flags & inspect.CO_GENERATOR), bool(code.co_flags & inspect.CO_GENERATOR))

nested = [c for c in make_helper.__code__.co_consts if inspect.iscode(c)]
print(len(nested), nested[0].co_name, make_helper().__code__.co_qualname)
print(1000 in make_helper.__code__.co_consts, 1000 in nested[0].co_consts)
print(outer())
print(snapshot_demo())
```

**Example**: the first line is

```
measure 2 ('a', 'b', 'first', 'total', 'label', 'second')
```

Write in `answer.txt` all the lines the program prints, in order (15 lines).
