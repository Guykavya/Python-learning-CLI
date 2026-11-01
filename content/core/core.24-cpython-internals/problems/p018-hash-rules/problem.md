# The rules of hashing

A dict (or set) finds a key by computing `hash(key)`, jumping to the slot that hash points to,
and comparing keys there with `==`. That only works if two promises hold:

1. **Equal objects have equal hashes.** If `a == b`, then `hash(a) == hash(b)`. (Different objects
   *may* share a hash; that is a collision, and `==` sorts it out.)
2. **A key's hash never changes while it is in a dict.** Otherwise the dict looks in the wrong slot.

That is why mutable built-ins (`list`, `dict`, `set`) are unhashable, and why a class that defines
`__eq__` without `__hash__` gets `__hash__ = None` and becomes unhashable too.

Two facts that are the same on every Python version: `hash()` of a small `int` is the int itself,
and `hash(-1) == -2`, because at C level `-1` means "an error happened", so CPython never returns
it as a hash.

Copy `starter.py` to `solution.py` and write:

**`check_hashable(obj)`** returns `True` if `hash(obj)` works and `False` if it raises `TypeError`.
Note that a tuple is hashable only if everything inside it is.

**`class Point`** with `Point(x, y)`, attributes `x` and `y`, usable as a dict key: equal
coordinates mean `==` and the same hash, and it is **immutable**: `p.x = 5` (or setting any
attribute) raises `AttributeError`. `repr(Point(1, 2))` is `'Point(1, 2)'`. Any correct technique
is fine (`__slots__` with `__setattr__`, properties, a frozen dataclass, ...).

**`lost_keys(d)`** returns, in iteration order, the keys of dict `d` that iteration can see but a
lookup can no longer find (`key in d` is `False`). That happens when a key object was changed
after insertion so that its hash changed.

**`hash_collisions(values)`** groups the values by `hash()`. For every hash shared by at least
two values that are **not equal** to each other, return a list of those values: keep only the
first of several equal values, in input order. Return the groups in order of the first value of
each group.

**Example**

```python
check_hashable((1, "a"))        # True
check_hashable((1, [2]))        # False: the list inside is unhashable

{Point(1, 2): "here"}[Point(1, 2)]    # 'here'

class Tag:
    def __init__(self, name):
        self.name = name
    def __eq__(self, other):
        return isinstance(other, Tag) and self.name == other.name
    def __hash__(self):
        return len(self.name)

t = Tag("ab")                   # hash 2
d = {t: "found"}
t.name = "abc"                  # now hash 3: the dict looks in the wrong slot
t in d                          # False
lost_keys(d)                    # [t]

hash_collisions([1, -1, 1.0, True, -2, 5])
# [[-1, -2]]   1, 1.0 and True share a hash but are all equal, so they are one value
```
