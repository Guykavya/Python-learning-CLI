## Approach

`@runtime_checkable` lets `isinstance(x, Proto)` work. The runtime check is shallow: for a method member it asks "does the object have an attribute with this name?", for a data member the same. It never looks at signatures, return types or the type of `name`. So:

- `total_area` uses `isinstance(thing, HasArea)` and trusts `area()` to return a number. The checker is what verifies the return type, and only if the code is checked.
- `names_of` needs an extra `isinstance(thing.name, str)`: `isinstance(thing, Named)` is `True` for `Pet()` whose `name` is `42`. Because of `and`, the second test only runs after the first has proved that `.name` exists.
- `classify` stores both answers first (clear, and each test runs once).

Note the two limits: `issubclass()` is **not** supported for protocols with data members (like `Named`), and the runtime check is slower than a normal `isinstance`.

## Code

```python
from collections.abc import Iterable
from typing import Protocol, runtime_checkable


@runtime_checkable
class HasArea(Protocol):
    def area(self) -> float: ...


@runtime_checkable
class Named(Protocol):
    name: str


def total_area(things: Iterable[object]) -> float:
    total = 0.0
    for thing in things:
        if isinstance(thing, HasArea):
            total += thing.area()
    return total


def names_of(things: Iterable[object]) -> list[str]:
    names: list[str] = []
    for thing in things:
        if isinstance(thing, Named) and isinstance(thing.name, str):
            names.append(thing.name)
    return names


def classify(thing: object) -> str:
    has_area = isinstance(thing, HasArea)
    has_name = isinstance(thing, Named)
    if has_area and has_name:
        return "both"
    if has_area:
        return "area"
    if has_name:
        return "name"
    return "neither"
```

## Complexity

All three are O(n) (O(1) for `classify`), plus the cost of each `area()` call.

## Another way

You can skip runtime protocols and use `getattr(thing, "name", None)` plus `isinstance(..., str)`, or try the call and catch `AttributeError` (EAFP, core.07). `runtime_checkable` is most useful when you want the *same* name to serve both the type checker and a runtime test, as in plugin loaders or argument validation.
