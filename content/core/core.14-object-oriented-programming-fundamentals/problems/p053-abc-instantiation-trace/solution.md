## Approach

When a class is created, `ABCMeta` collects every name marked `@abstractmethod` that is not
overridden yet into `__abstractmethods__`. Calling the class checks that set: if it is not empty,
`TypeError`. Overriding can happen in any class along the way (chapter section 16). `register()`
only records a virtual subclass for `isinstance`/`issubclass`; it does not copy methods and does not
change the MRO.

## Step by step

1. `make(Shape)`: two abstract methods left -> `Shape -> cannot instantiate`.
2. `make(Square, 2)`: `Square` overrides `area` only; `name` is still abstract ->
   `Square -> cannot instantiate`. (`__init__` never runs: the check happens first.)
3. `make(NamedSquare, 3)`: `area` from `Square`, `name` from `NamedSquare`; nothing left ->
   `NamedSquare -> ok`.
4. `make(Triangle)`: both overridden -> `Triangle -> ok`.
5. `sq.describe()`: `describe` is a normal method of `Shape`; `name()` is `"square"`, `area()` is
   `3 * 3` -> `square has area 9`.
6. `tri.describe()`: `Triangle.area` calls `super().area()`, the body of the abstract method, which
   returns `0`; `0 + 6 = 6` -> `triangle has area 6`.
7. `sorted(Shape.__abstractmethods__)` -> `['area', 'name']`.
8. `Square` still misses `name` -> `['name']`.
9. `NamedSquare` misses nothing -> `[]`.
10. `isinstance(sq, Shape)` is `True` (real subclass). `Blob` is not related to `Shape` yet, even
    though it has both methods: ABCs do not check method names by themselves -> `True False`.
11. `Shape.register(Blob)`; `make(Blob)`: `Blob` is a plain class, not created by `ABCMeta`, so no
    abstract check -> `Blob -> ok`.
12. Now `isinstance(blob, Shape)` and `issubclass(Blob, Shape)` are both `True` -> `True True`.
13. But `Blob.__mro__` is still `(Blob, object)`, so `Shape in Blob.__mro__` is `False`, and `blob`
    did **not** get `describe` -> `False False`.
14. `Shape.area(sq)` calls the abstract method's body directly with `self = sq` -> `0`.

## Output

```text
Shape -> cannot instantiate
Square -> cannot instantiate
NamedSquare -> ok
Triangle -> ok
square has area 9
triangle has area 6
['area', 'name']
['name']
[]
True False
Blob -> ok
True True
False False
0
```

## Complexity

Not applicable.

## Another way

`register()` is a promise you make **without** any check: Python believes you that `Blob` behaves like a
`Shape`. If you want the methods too, inherit for real (`class Blob(Shape)`). `collections.abc` uses
both ideas: `list` is registered as a `MutableSequence`, and some ABCs like `Iterable` even recognise
classes automatically when they define `__iter__`.
