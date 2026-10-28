# Trace: @contextmanager, errors and return

A generator marked with `@contextmanager` is split by `yield`: the code before it is `__enter__`, the code
after it is `__exit__`. If the `with` body raises, the error is thrown **into the generator at the yield**.
The generator may handle it (swallow it) or let it go on.

```python
import sys
from contextlib import contextmanager


@contextmanager
def section(name, swallow=()):
    print("enter", name)
    try:
        yield name.upper()
    except swallow as error:
        print("swallowed", type(error).__name__)
    finally:
        print("exit", name)


def work():
    with section("a") as a:
        print("got", a)
        with section("b", swallow=KeyError) as b:
            print("got", b)
            {}["x"]
            print("not printed")
        print("after b")
        return "done"
    print("not printed either")


print(work())
try:
    with section("c", swallow=KeyError):
        print("in c")
        raise ValueError("bad")
except ValueError as error:
    print("outer caught", error)
    print("log line", file=sys.stderr)
print("end")
```

Write exactly what the program prints to **standard output**, one line for each printed line, in `answer.txt`.
The program never ends with a traceback. Lines sent to `sys.stderr` do not count.
