## Approach

`shout` is the outer function. It defines `wrapper`, which closes over `func`. `wrapper` collects any
arguments with `*args, **kwargs`, passes them on unchanged, and upper-cases the result. `shout` returns
`wrapper` without calling it.

`loud_greet = shout(greet)` is exactly what `@shout` does for you. The only difference is that `@shout` puts
the wrapper back under the **same** name, so the original is no longer reachable by that name.

## Code

```python
def shout(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result.upper()
    return wrapper


def greet(name):
    return "hello, " + name


loud_greet = shout(greet)
```

## Complexity

O(1) to decorate. Each call costs one call of `func` plus O(k) for `upper()` on a result of length k.

## Another way

Write `@shout` above a function. Then `greet = shout(greet)` happens for you at definition time. Here we
kept two names on purpose, so you can see both functions side by side.
