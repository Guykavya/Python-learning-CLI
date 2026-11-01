# Small protocols

**Interface segregation**: do not force a class (or a function) to depend on methods it does not
use. The fat `Storage` ABC in `starter.py` demands five methods. A `ReadOnlyStorage` must
fake three of them with `raise NotImplementedError`, and `copy_all(src, dst)` claims to need a
full `Storage` for both sides when it only reads one and writes the other.

Python's answer: small `typing.Protocol` classes. A Protocol describes "anything that has these
methods" (duck typing, but written down and checkable). A class does **not** inherit from it; it
only has to have the methods.

```python
@runtime_checkable            # lets isinstance(x, Reader) check that the methods exist
class Reader(Protocol):
    def read(self, key): ...
    def keys(self): ...
```

Copy `starter.py` to `solution.py` and:

1. Define `Reader` (methods `read(key)` and `keys()`) and `Writer` (method `write(key, value)`) as
   `@runtime_checkable` Protocols. Declare **only** those methods.
2. Remove the fat `Storage` ABC, `MemoryStorage` and `ReadOnlyStorage` (no `ABC`, no abstract methods,
   no stubs that raise `NotImplementedError`).
3. Keep `copy_all(src, dst)`, `dump(src)` and `save_all(dst, items)` with the same behaviour, but
   **annotate** each parameter with the smallest Protocol it needs (`src: Reader`, `dst: Writer`).

The tests use classes that have only some of the methods: a read-only `Source`, a write-only
`Sink`, a `Both`, and an `OnlyRead` that has `read` but not `keys` (so it is **not** a `Reader`).

**Example**

```python
class Sink:
    def __init__(self): self.entries = []
    def write(self, key, value): self.entries.append((key, value))

isinstance(Sink(), Writer)      # True   (it has write)
isinstance(Sink(), Reader)      # False
save_all(Sink(), {"a": "1"})    # 1
```
