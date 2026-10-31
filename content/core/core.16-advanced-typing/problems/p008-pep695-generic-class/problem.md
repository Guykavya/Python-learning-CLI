# Generic class with the Python 3.12 syntax

Python 3.12 added a short way to write generics. No `TypeVar` line, no `Generic[...]`: the type
parameters go in square brackets right after the name.

```python
class Box[T]:                      # T is local to this class
    def map[U](self, func: Callable[[T], U]) -> Box[U]:   # U is local to this method
        ...

def biggest[N: (int, float)](a: N, b: N) -> N:       # constrained: int or float
    ...
```

In `solution.py`, **using this syntax** (the tests look at `__type_params__`, which is empty for
the old `Generic[T]` style), write:

**`class Box[T]`** holds one value.

- `__init__(self, value: T) -> None`; the value is stored as `self.value`.
- `get(self) -> T`: the value.
- `map[U](self, func: Callable[[T], U]) -> Box[U]`: a **new** `Box` that holds `func(self.value)`.
- `__repr__`: `Box(5)` or `Box('x')` (use `!r` for the value).
- `__eq__`: two boxes are equal if they are both `Box` and hold equal values. (Return
  `NotImplemented` for other types.) Add `__hash__` too: `hash(("Box", self.value))`.

**`biggest[N: (int, float)](a: N, b: N) -> N`**: the larger of two numbers (the first one if equal).
The type parameter `N` must be a **constrained** parameter with exactly the constraints
`(int, float)`.

Import `Callable` from `collections.abc`.

**Example**

```python
b = Box(5)             # Box[int]
b.get()                # 5
b.map(str)             # Box('5')       a type checker says: Box[str]
b.map(lambda n: n * 2).get()   # 10
Box(1) == Box(1)       # True
Box(1) == 1            # False
biggest(3, 7)          # 7
biggest(2.5, 1.0)      # 2.5
```
