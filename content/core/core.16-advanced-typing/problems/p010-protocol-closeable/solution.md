## Approach

A `Protocol` class lists the members a type needs. A type "is a" `Closeable` if it has a `close(self) -> None` method, no matter what it inherits from. The body `...` is a placeholder: nobody calls the protocol's own method. This is *structural* typing; the checker compares the **shape** of your class with the shape of the protocol.

`close_all` is a normal loop. `close_quietly` uses `except Exception` and not a bare `except:` so that `KeyboardInterrupt` and `SystemExit` still get through; those are not "failures to close", they are the user or the interpreter asking to stop.

## Code

```python
from collections.abc import Iterable
from typing import Protocol


class Closeable(Protocol):
    def close(self) -> None: ...


def close_all(items: Iterable[Closeable]) -> int:
    count = 0
    for item in items:
        item.close()
        count += 1
    return count


def close_quietly(item: Closeable) -> bool:
    try:
        item.close()
    except Exception:
        return False
    return True
```

## Complexity

`close_all`: O(n) calls. `close_quietly`: O(1) plus the cost of `close()`. Both use O(1) extra space.

## Another way

`contextlib.closing(item)` is the standard library's way to turn "has `close()`" into a `with` block, and it is typed with the same idea (`SupportsClose`). For `close_all`, `contextlib.ExitStack` can close many objects and still close the rest when one fails. A *base class* `class Closeable(ABC)` would work too, but every user class would have to inherit from it, including classes you do not control, like `io.StringIO`.
