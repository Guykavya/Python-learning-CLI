## Approach

`sys.getsizeof` reports one object's own memory. A slotted instance stores its three references
inside itself, so that number is the whole story. An ordinary instance keeps them in a separate
dictionary object, so its real cost is the object plus that dict. Building all instances first
and keeping them in lists makes sure we measure `n` live objects (and not one object reused).

## Code

```python
import sys


class Plain:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


class Slotted:
    __slots__ = ("x", "y", "z")

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


def instance_size(obj):
    size = sys.getsizeof(obj)
    if hasattr(obj, "__dict__"):
        size += sys.getsizeof(obj.__dict__)
    return size


def compare_memory(n):
    plains = [Plain(i, i, i) for i in range(n)]
    slotted = [Slotted(i, i, i) for i in range(n)]
    return (
        sum(instance_size(obj) for obj in plains),
        sum(instance_size(obj) for obj in slotted),
    )
```

On Python 3.14 (64-bit) one `Slotted` is 56 bytes: a 16-byte object header, 16 bytes of bookkeeping
for the garbage collector and three 8-byte references. One `Plain` object is 48 bytes, and the
size reported for its dict varies, from about 100 to about 300 bytes in the same run, depending on
how the dict shares its keys with the other instances. That variation is exactly why the tests only
compare totals. Remember too that recent versions avoid creating the dict at all while nobody asks
for `__dict__` (attribute values are stored in the object, the keys are shared by all instances of
the class). So this measurement exaggerates the saving on 3.12+. Use `tracemalloc` (core.20) to
measure what a whole program really allocates.

## Complexity

O(n) time and memory.

## Another way

Measure with `tracemalloc` instead of `getsizeof`, which counts what the allocator really gave
out, including things `getsizeof` cannot see:

```python
import tracemalloc

def allocated_by(make, n):
    tracemalloc.start()
    before = tracemalloc.take_snapshot()
    objs = [make(i) for i in range(n)]
    after = tracemalloc.take_snapshot()
    tracemalloc.stop()
    return sum(s.size_diff for s in after.compare_to(before, "filename")), objs
```

The result includes the list holding the objects and depends on the version, so compare two
measurements with each other rather than with a fixed number.
