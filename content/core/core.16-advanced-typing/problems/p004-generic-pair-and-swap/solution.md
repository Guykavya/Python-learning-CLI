## Approach

`Generic[A, B]` gives the class two type parameters, in that order. `Pair[str, int]` means `A = str`, `B = int`. Methods may mention both. The interesting methods **change** the types: `swap` returns `Pair[B, A]` (the two parameters trade places), `map_first` introduces a third variable `C` (the result type of `func`) and returns `Pair[C, B]`.

`C` appears only in the method, not in the class: it is a *method-level* type variable, solved each time the method is called. `frozen=True` makes the pair immutable, so every method returns a new `Pair`, which is also what makes "the type changes" honest: the old object keeps its old type.

The string hints `"Pair[B, A]"` are forward references: the class `Pair` is not defined yet when its own method hints are evaluated (on older Pythons). `get_type_hints` turns them back into real types.

## Code

```python
from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


@dataclass(frozen=True)
class Pair(Generic[A, B]):
    first: A
    second: B

    def swap(self) -> "Pair[B, A]":
        return Pair(self.second, self.first)

    def map_first(self, func: Callable[[A], C]) -> "Pair[C, B]":
        return Pair(func(self.first), self.second)

    def map_second(self, func: Callable[[B], C]) -> "Pair[A, C]":
        return Pair(self.first, func(self.second))


def swap_tuple(p: tuple[A, B]) -> tuple[B, A]:
    a, b = p
    return (b, a)
```

## Complexity

Every method is O(1) (plus the cost of `func`).

## Another way

With Python 3.12+: `class Pair[A, B]:` and `def map_first[C](self, func: Callable[[A], C]) -> Pair[C, B]:`, no `TypeVar` lines and no quotes needed (annotations are lazy). Use `typing.Self` only when the type does *not* change; here it changes, so `Pair[B, A]` is the honest answer.
