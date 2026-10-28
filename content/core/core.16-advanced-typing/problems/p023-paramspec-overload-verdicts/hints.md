## Hint 1

First work out the type of the **decorated** `add` and `sub`. `logged` takes `Callable[P, R]` and returns `Callable[P, R]`. What does `P` capture? `sloppy` returns `Callable[..., Any]`. What does `...` say about the parameters, and what does `Any` say about the result?

## Hint 2

After `@logged`, `add` still has the signature `(a: int, b: int = 0) -> int`, so a call is checked against that: names, number of arguments, types. After `@sloppy`, `sub` is `Callable[..., Any]`: any arguments are fine, and the result is `Any`.

## Hint 3

For `parse`, mypy tries the overloads from top to bottom and uses the first one that fits the argument. If none fits, it reports an error (it does not fall back to the implementation signature, which is invisible to callers).
