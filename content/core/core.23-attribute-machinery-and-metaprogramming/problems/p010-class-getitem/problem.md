# `TypedList[int]` with `__class_getitem__`

`list[int]` works because `list` defines `__class_getitem__`: writing `Cls[x]` calls
`Cls.__class_getitem__(x)` (an implicit classmethod). For built-ins it returns a
`types.GenericAlias`, a label for type checkers that **checks nothing at run time**: you can
still append a string to a `list[int]()`.

Here you make subscription return a **real subclass that does check**.

Copy `starter.py` to `solution.py` and finish `TypedList(list)`:

- `TypedList.item_type` is `object`, so a plain `TypedList` accepts anything.
- `TypedList[T]` returns a subclass of `TypedList` named `"TypedList[<T's name>]"` whose
  `item_type` is `T`. Asking for the same `T` again returns **the same class** (keep a cache),
  so `TypedList[int] is TypedList[int]`.
- `T` must be a class; otherwise raise `TypeError` (`TypedList[3]`).
- `__init__(self, items=())` and `append(self, item)` raise `TypeError` for an item that is not
  an instance of `item_type`. The message names the expected and the actual type. Nothing is
  added when an item is rejected. `items` may be a generator.

(Checking only `__init__` and `append` is enough for this drill; `extend`, `insert` and
`lst[i] = x` would need the same treatment in real code.)

**Example**

```python
nums = TypedList[int]([1, 2])
nums.append(3)
nums                      # [1, 2, 3]
nums.append("4")          # TypeError: TypedList[int] expects int, got str
TypedList[int] is TypedList[int]     # True
TypedList[int].__name__   # 'TypedList[int]'
TypedList([1, "a"])       # [1, 'a']   (no type given: anything goes)
```
