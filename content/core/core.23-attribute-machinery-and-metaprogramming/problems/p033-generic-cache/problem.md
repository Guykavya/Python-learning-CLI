# A cached generic `Box` with `__class_getitem__`

`list[int]` only *describes* a list of ints: `list[int]()` happily stores strings. Here you will
build a container whose subscription creates a **real class** that checks its contents at run
time. `Box[int]` is a subclass of `Box` that only accepts ints.

Copy `starter.py` to `solution.py` and write the class `Box`:

**The container.**

- `Box()` makes an empty box. `put(value)` stores one value (replacing the old one) and
  `get()` returns it; `get()` on an empty box raises `LookupError("box is empty")`.
- The class attribute `item_type` says what a box accepts. On plain `Box` it is `object` (anything).
- `put` checks `isinstance(value, item_type)` and otherwise raises
  `TypeError("Box[int] accepts int, not str")` (class name, expected type name, actual type name).
- `repr(box)` is `Box[int](5)` when full and `Box[int](empty)` when empty (the class name first).

**Subscription.** `Box[T]` calls `Box.__class_getitem__(T)` and must return a class:

- a new subclass of the class being subscripted, created with `type()`, whose `__name__` is
  `Box[int]` and whose `item_type` is `int`;
- **cached**: `Box[int] is Box[int]`. Two different classes must never share a cache entry:
  for `class Special(Box)`, `Special[int]` is a subclass of `Special` named `Special[int]`, not `Box[int]`;
- `T` may be any class, including another parameterised box (`Box[Box[int]]`, named
  `Box[Box[int]]`), or a generic alias like `list[int]`: then the box is named `Box[list[int]]`,
  and `put` checks only the outer type (`isinstance(value, list)`), because an alias cannot be
  used with `isinstance`. Use `types.GenericAlias` to recognise aliases and their `__origin__`;
- `Box[int, str]` raises `TypeError("Box takes exactly one type")`;
- `Box[3]` (not a class or alias) raises `TypeError`;
- an already parameterised box cannot be subscripted again: `Box[int][str]` raises `TypeError`.

Subclassing a parameterised box works: `class IntBox(Box[int])` accepts only ints.

**Example**

```python
b = Box[int]()
b.put(5)
b.get()                        # 5
b.put("five")                  # TypeError: Box[int] accepts int, not str
Box[int] is Box[int]           # True
issubclass(Box[int], Box)      # True
Box[list[int]]().put([1, 2])   # fine; put("x") would raise TypeError
Box[Box[int]]().put(b)         # a box of int-boxes
repr(b)                        # 'Box[int](5)'
```
