# Your first Protocol: `Closeable`

Files, sockets, database connections: all can be closed with `.close()`, but they share no
common parent class. A **Protocol** describes a type by what it can **do**, not by what it
inherits from. This is called *structural typing*, and it is duck typing that the type checker
can verify.

In `solution.py` write:

```python
class Closeable(Protocol):
    def close(self) -> None: ...
```

and two functions that use it:

1. `close_all(items: Iterable[Closeable]) -> int`: call `close()` on every item, in order, and
   return how many items were closed. If an item raises while closing, let the exception go
   (do not hide it).
2. `close_quietly(item: Closeable) -> bool`: call `close()`; return `True` if it worked and
   `False` if it raised any `Exception` (the exception is swallowed).

Import `Protocol` from `typing` and `Iterable` from `collections.abc`.

The tests pass objects that do **not** inherit from `Closeable` (a `StringIO`, a few plain
classes). That is the point: `Closeable` is satisfied by shape. The tests also look at your
protocol with `typing.get_protocol_members` and check the hints of your functions.

**Example**

```python
import io

class Conn:
    def close(self) -> None:
        print("conn closed")

close_all([io.StringIO(), Conn()])   # prints "conn closed"; returns 2
close_quietly(Conn())                # prints "conn closed"; returns True
```
