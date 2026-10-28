# A logging decorator that keeps its signature

A decorator wrapped in `(*args, **kwargs)` hides the real signature from the type checker: every
decorated function becomes `Callable[..., Any]`. A `ParamSpec` fixes that. It captures the
**whole parameter list** of the function and passes it on unchanged.

In `solution.py` write:

1. `CALL_LOG: list[str] = []` (module level).
2. `logged(func)`, a decorator. Every call of the decorated function first appends one string
   to `CALL_LOG`, then calls the original and returns its result. The string is the function's
   name, then the arguments in parentheses, positional first, then keywords:
   `"add(1, 2)"`, `"greet('Ada', punctuation='!')"` (use `repr` for each value).
3. `logged_as(prefix)`, a decorator **factory**: `@logged_as("db")` works like `logged` but
   the string starts with `"db: "`, e.g. `"db: add(1, 2)"`.

Type hints required (the tests read them at runtime):

```python
P = ParamSpec("P")
R = TypeVar("R")

def logged(func: Callable[P, R]) -> Callable[P, R]: ...
def logged_as(prefix: str) -> Callable[[Callable[P, R]], Callable[P, R]]: ...
```

The wrapper function inside takes `*args: P.args, **kwargs: P.kwargs` and returns `R`.
Use `functools.wraps` so the decorated function keeps its name and its real signature.

**Example**

```python
@logged
def add(a: int, b: int) -> int:
    return a + b

add(1, 2)       # 3
CALL_LOG        # ["add(1, 2)"]
add(1, b=5)     # 6; CALL_LOG now ends with "add(1, b=5)"
```

**Remember**: with `Callable[P, R]` in and `Callable[P, R]` out, a checker still knows that
`add("x")` is an error after decoration. With `Callable[..., Any]` it would not.
