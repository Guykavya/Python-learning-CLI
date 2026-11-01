## Approach

Move the part that varies (the formula) out of the function and into a dict, so the part that
stays the same (look up and call) never needs to change.

- `register("circle")` runs first and returns `decorator`; Python then calls `decorator(function)`
  because of the `@`. The decorator stores the function and returns it, so the name `_circle` still
  works as a normal function.
- Raising on a duplicate name means a typo (two shapes both called `"rect"`) shows up at once instead of
  silently replacing a formula.
- `area` converts the `KeyError` into a `ValueError` with a useful message; `from None` hides the
  confusing "during handling of the above exception" chain.

## Code

```python
import math

_AREAS = {}


def register(name):
    def decorator(func):
        if name in _AREAS:
            raise ValueError(f"shape already registered: {name}")
        _AREAS[name] = func
        return func

    return decorator


def shape_names():
    return sorted(_AREAS)


@register("circle")
def _circle(shape):
    return math.pi * shape["r"] ** 2


@register("rect")
def _rect(shape):
    return shape["w"] * shape["h"]


@register("square")
def _square(shape):
    return shape["side"] ** 2


def area(shape):
    kind = shape["type"]
    try:
        func = _AREAS[kind]
    except KeyError:
        raise ValueError(f"unknown shape: {kind}") from None
    return func(shape)
```

## Complexity

`area` is O(1) (one dict lookup) instead of O(number of shapes) for the chain. Registering is O(1).

## Another way

Make each shape a small class with an `area()` method and call `shape.area()` (polymorphism);
that is open/closed too, with the dispatch done by Python. A registry is better when the
shapes are plain data (dicts from JSON) and the formulas live elsewhere. `functools.singledispatch`
is a built-in registry that dispatches on the **type** of the first argument instead of a name.
