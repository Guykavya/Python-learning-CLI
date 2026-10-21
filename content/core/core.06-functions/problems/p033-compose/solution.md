## Approach

`compose` builds and returns a closure. The inner function remembers `funcs` (a tuple) from the
enclosing scope. When it is called, it threads a value through the functions from last to first.
With an empty tuple the loop does nothing, so the identity case is automatic.

## Code

```python
def compose(*funcs):
    """Return a function x -> funcs[0](funcs[1](...funcs[-1](x)))."""
    def composed(x):
        for f in reversed(funcs):
            x = f(x)
        return x
    return composed
```

## Complexity

Creating the composition is O(1); calling it costs one call per function.

## Another way

`functools.reduce` can fold the functions into one:
```python
from functools import reduce
def compose(*funcs):
    return reduce(lambda f, g: lambda x: f(g(x)), funcs, lambda x: x)
```
Clever and compact, but much harder to read.
