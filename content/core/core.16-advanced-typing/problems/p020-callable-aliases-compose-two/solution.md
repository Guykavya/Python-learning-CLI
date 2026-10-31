## Approach

A function type is `Callable[[param types...], return type]`. Giving a long one a name (an alias)
keeps signatures short. `compose_two` is generic: it relates three types with three `TypeVar`s.
`f: A -> B` and `g: B -> C` fit end to end, so the result is `A -> C`. The checker uses the
`TypeVar`s to link the call site: `compose_two(len, str)` becomes `Callable[[Sized], str]`.

## Code

```python
from collections.abc import Callable
from typing import TypeVar

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")

IntTransform = Callable[[int], int]
IntPredicate = Callable[[int], bool]


def count_matching(items: list[int], pred: IntPredicate) -> int:
    return sum(1 for item in items if pred(item))


def apply_all(x: int, steps: list[IntTransform]) -> int:
    for step in steps:
        x = step(x)
    return x


def compose_two(f: Callable[[A], B], g: Callable[[B], C]) -> Callable[[A], C]:
    def composed(x: A) -> C:
        return g(f(x))

    return composed
```

## Complexity

`count_matching` and `apply_all` are O(n) calls. `compose_two` is O(1) to build and O(1) extra per call.

## Another way

`type IntTransform = Callable[[int], int]` (Python 3.12+) is the modern alias form, and
`def compose_two[A, B, C](f: Callable[[A], B], g: Callable[[B], C]) -> Callable[[A], C]` removes
the `TypeVar` lines. `functools.reduce` can write `apply_all` in one line, but the loop is clearer.
