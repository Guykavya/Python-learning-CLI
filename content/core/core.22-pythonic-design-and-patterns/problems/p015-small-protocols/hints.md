## Hint 1

For each function, list the methods it really calls on each parameter. `copy_all` calls `keys`
and `read` on `src`, and only `write` on `dst`. Group methods that are always used together
into one small interface. How many interfaces do you need, and what do you name them?

## Hint 2

```
from typing import Protocol, runtime_checkable

@runtime_checkable
class Reader(Protocol):   def read(self, key): ...   def keys(self): ...
@runtime_checkable
class Writer(Protocol):   def write(self, key, value): ...

def copy_all(src: Reader, dst: Writer): ...   (body unchanged)
def dump(src: Reader): ...
def save_all(dst: Writer, items): ...
```
Delete `Storage`, `MemoryStorage`, `ReadOnlyStorage`. What happens to `isinstance(x, Reader)`
if you forget `@runtime_checkable`?
