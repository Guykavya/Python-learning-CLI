## Approach

Each curried function is a closure over two **immutable-in-practice** values: a tuple of saved
positional arguments and a dict of saved keywords. Calling it never changes them; it builds new
ones and either finishes the job or makes a new closure through `make`. That is why `base(3)` and
`base(10)` cannot disturb each other.

`inspect.signature(func).parameters` lists the parameters in order. A parameter is required and
positional when its kind is `POSITIONAL_ONLY` or `POSITIONAL_OR_KEYWORD` and its default is the
special marker `p.empty`.

## Code

```python
import inspect
from functools import wraps


def curry(func):
    positional = (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
    needed = sum(
        1
        for p in inspect.signature(func).parameters.values()
        if p.kind in positional and p.default is p.empty
    )

    def make(saved_args, saved_kwargs):
        @wraps(func)
        def curried(*args, **kwargs):
            all_args = saved_args + args
            all_kwargs = {**saved_kwargs, **kwargs}
            if len(all_args) >= needed:
                return func(*all_args, **all_kwargs)
            return make(all_args, all_kwargs)
        return curried

    return make((), {})
```

## Complexity

Each call copies the saved arguments: O(a + k) for a positional and k keyword arguments, which
is tiny. Counting the parameters happens once.

## Another way

`functools.partial` already stores "a function plus some arguments", so the saved state can live
in a partial instead of in `make`'s closure:

```python
def curry(func):
    needed = ...  # as above

    def curried(*args, **kwargs):
        if len(args) >= needed:
            return func(*args, **kwargs)
        return wraps(func)(partial(curried, *args, **kwargs))
    return wraps(func)(curried)
```

Calling `partial(curried, 2)(3)` runs `curried(2, 3)`, which counts both arguments. Partials
also never change their stored arguments, so branches stay independent here too.
