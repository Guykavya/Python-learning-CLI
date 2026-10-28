## Approach

Python runs the file from top to bottom. `print("start")` comes first. Then it reaches `@loud def hello`.
It builds the function and at once calls `loud(hello)`. That prints `decorating hello` and
`returning wrapper`. The body of `wrapper` does **not** run yet. The name `hello` now points at `wrapper`.

Each `hello()` call runs `wrapper`: `before hello`, then the original body (`hello body`), then
`after hello`. Only then does the outer `print` show the returned `hi`. The decorator body is **not** run
again on the second call; decoration happens once.

`wrapper` was made without `functools.wraps`, so `hello.__name__` is `wrapper`. Inside `wrapper`,
`func.__name__` is still `hello`, because `func` is the original function.

## Output

```text
start
decorating hello
returning wrapper
defined
before hello
hello body
after hello
hi
before hello
hello body
after hello
hi
wrapper
```

## Complexity

O(1).

## Another way

Put `print("about to define")` just above the `@` line and run the file. You will see that the decorator's
own prints come right after it, before any call.
