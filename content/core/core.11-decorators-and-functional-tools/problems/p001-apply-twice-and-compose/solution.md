## Approach

`apply_twice` passes the first result straight back into `f`: `f(f(x))`.

`compose` defines an inner function `composed`. The inner function remembers `f` and `g` from the enclosing
call (a closure). `compose` returns `composed` itself, the function object, so nothing runs until someone
calls it.

## Code

```python
def apply_twice(f, x):
    return f(f(x))


def compose(f, g):
    def composed(x):
        return f(g(x))
    return composed
```

## Complexity

`apply_twice` costs two calls of `f`. `compose` is O(1) to build; each call of the result costs one call of `g` and one of `f`.

## Another way

`compose` can return a lambda: `return lambda x: f(g(x))`. It works the same way. The named inner function
reads better in a traceback and is the exact shape a decorator has: an outer function that returns an inner one.
