## Approach

Look at what each function *uses*, not at what some big class *offers*. `copy_all` needs a thing
you can read and list, and a thing you can write to. Two small Protocols say exactly that, and
any class with those methods fits without inheriting anything. A class that can only read is
a perfectly good `Reader`; it no longer has to pretend it can write.

`@runtime_checkable` lets `isinstance(obj, Reader)` check that the **methods exist** (it does not
check their signatures or what they do). Without it, `isinstance` raises `TypeError`.

## Code

```python
from typing import Protocol, runtime_checkable


@runtime_checkable
class Reader(Protocol):
    def read(self, key): ...

    def keys(self): ...


@runtime_checkable
class Writer(Protocol):
    def write(self, key, value): ...


def copy_all(src: Reader, dst: Writer):
    count = 0
    for key in src.keys():
        dst.write(key, src.read(key))
        count += 1
    return count


def dump(src: Reader):
    return {key: src.read(key) for key in src.keys()}


def save_all(dst: Writer, items):
    for key, value in items.items():
        dst.write(key, value)
    return len(items)
```

## Complexity

No change at run time: O(number of keys). The design cost is zero lines of inheritance and fewer
methods to implement.

## Another way

Keep one ABC but split it: `class Reader(ABC)`, `class Writer(ABC)`; classes must then inherit from
them (nominal typing). Protocols are structural: no inheritance needed, which is more Pythonic
and lets you use classes from other libraries. For a class that does everything, define
`class ReadWriter(Reader, Writer, Protocol): ...` by combining small ones.
