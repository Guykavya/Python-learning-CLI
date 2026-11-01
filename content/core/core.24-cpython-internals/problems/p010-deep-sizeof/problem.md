# Deep size of a container

`sys.getsizeof(obj)` returns the number of bytes of **that one object**. For a container it
counts the container's own memory (its header and its array of pointers), but **not** the
objects it points to:

```python
import sys
names = ["a" * 1000, "b" * 1000]
sys.getsizeof(names)        # small, about 70 bytes: just the list and two pointers
sys.getsizeof(names[0])     # about 1,000 bytes: the string itself
```

(The exact numbers depend on the Python version and platform, so never rely on them.)

Copy `starter.py` to `solution.py` and write **`deep_size(obj)`**: the total of `sys.getsizeof`
over `obj` and every object reachable from it through containers.

- Look inside `list`, `tuple`, `set`, `frozenset` and `dict` (both keys and values), at any depth.
- Any other object counts with its own `sys.getsizeof` only; do not look inside it.
- Count each object **once**, even if it is reachable many times. Decide "same object" by
  `id()`, not by `==`: two equal ints that are separate objects take memory twice.
- A container may contain itself (a cycle); your function must still finish.

**Example**

```python
import sys
a = int("1000")
b = int("1000")          # equal to a, but a separate object
data = [a, b, a]
deep_size(data) == sys.getsizeof(data) + sys.getsizeof(a) + sys.getsizeof(b)   # True

loop = []
loop.append(loop)
deep_size(loop) == sys.getsizeof(loop)                                         # True
```
