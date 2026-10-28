# Trace: order of `__enter__` and `__exit__` with an exception

This is the trace assessment of the module. Nested `with` blocks enter from the outside in and exit
from the inside out. When the body raises, each `__exit__` sees the exception, and a manager whose
`__exit__` returns `True` swallows it, so the outer managers see **nothing**.

Read the code and write down exactly what it prints.

```python
from contextlib import contextmanager


class Tracer:
    def __init__(self, name, swallow=False):
        self.name = name
        self.swallow = swallow

    def __enter__(self):
        print("enter", self.name)
        return self.name.upper()

    def __exit__(self, exc_type, exc, tb):
        print("exit", self.name, exc_type.__name__ if exc_type else None)
        return self.swallow


@contextmanager
def gen(name):
    print("setup", name)
    try:
        yield name * 2
    except KeyError:
        print("gen caught KeyError", name)
    finally:
        print("cleanup", name)


def run(label, body):
    print("== " + label)
    try:
        body()
    except Exception as err:
        print("escaped", type(err).__name__)
    else:
        print("finished normally")


def one():
    with Tracer("a") as x:
        print("body", x)


def two():
    with Tracer("a") as x, Tracer("b") as y:
        print("body", x, y)
        raise ValueError("v")


def three():
    with Tracer("a"):
        with Tracer("b", swallow=True):
            raise ValueError("v")
        print("after b")


def four():
    with Tracer("a", swallow=True):
        with Tracer("b"):
            print("body")
            raise KeyError("k")
        print("never")
    print("after a")


def five():
    with gen("p") as v:
        print("body", v)
        raise KeyError("k")
    print("after p")


def six():
    with gen("q") as v:
        print("body", v)
        raise ValueError("v")
    print("after q")


for label, body in (("one", one), ("two", two), ("three", three),
                    ("four", four), ("five", five), ("six", six)):
    run(label, body)
```

In `answer.txt`, write the printed output, one line per printed line.

Facts you need:

- `with A() as x, B() as y:` is the same as a `with` inside a `with`: A is entered first and exited last.
- `__exit__` gets `exc_type` (the class, or `None`). `__exit__` returns `self.swallow`, a true value
  means "swallow the exception".
- `print("exit", "a", None)` prints `exit a None`.
- For a `@contextmanager` generator, a block that raises resumes the generator by raising that
  exception at the `yield`. If the generator catches it and ends normally, the exception is swallowed.
- `"p" * 2` is `"pp"`.

## Example of the format

```python
class T:
    def __enter__(self):
        print("in")
        return 1
    def __exit__(self, *args):
        print("out", args[0])

with T() as v:
    print("v is", v)
```

prints three lines: `in`, `v is 1`, `out None`.
