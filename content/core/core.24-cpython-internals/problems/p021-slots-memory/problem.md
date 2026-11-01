# How much do `__slots__` save?

An ordinary instance keeps its attributes in a dictionary, `obj.__dict__`. A class with
`__slots__ = ("x", "y", "z")` instead reserves exactly three fixed places inside the object itself
and has no `__dict__` at all. That is smaller, and it also forbids adding new attributes.

`sys.getsizeof(obj)` reports only the object's **own** memory. For an ordinary instance that does
not include the attribute dictionary, so to compare fairly you must add `sys.getsizeof(obj.__dict__)`.
(It never includes the attribute *values* either; they are the same for both classes here, so we
leave them out.)

Copy `starter.py` to `solution.py` and write:

- **`class Plain`**: `Plain(x, y, z)` stores three attributes the ordinary way.
- **`class Slotted`**: the same constructor and attributes, with `__slots__ = ("x", "y", "z")`.
- **`instance_size(obj)`**: `sys.getsizeof(obj)`, plus `sys.getsizeof(obj.__dict__)` if the object
  has a `__dict__`.
- **`compare_memory(n)`**: creates `n` `Plain` and `n` `Slotted` instances (keep them all alive in
  lists while you measure, values `(i, i, i)` for example) and returns the tuple
  `(plain_total, slotted_total)` of the sums of `instance_size` over each group.

**Version warning.** Every number below is a CPython detail that changes between versions
(3.11 to 3.14 changed how instance attributes are stored several times) and between 32- and 64-bit
builds. Even asking for `obj.__dict__` can change things, because recent versions create the
dictionary only when someone asks for it. The tests check relations only: slotted is smaller,
totals add up, and so on.

**Example**

```python
p, s = Plain(1, 2, 3), Slotted(1, 2, 3)
hasattr(s, "__dict__")       # False
instance_size(p)             # 344 in one run on Python 3.14, 64-bit (48 + 296): yours will differ
instance_size(s)             # 56 on Python 3.14, 64-bit
plain, slotted = compare_memory(1000)
plain, slotted               # (144000, 56000) in the same run: other Plain dicts were smaller
plain > slotted              # True on every version
s.w = 4                      # AttributeError: no slot for 'w'
```
