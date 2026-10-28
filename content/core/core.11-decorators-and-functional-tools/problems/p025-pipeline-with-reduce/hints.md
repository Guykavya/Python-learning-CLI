## Hint 1

`reduce(f, items, start)` does `acc = start`, then `acc = f(acc, item)` for each item. If the
items are the **functions** and the start is the **value**, what should `f(acc, step)` return?

## Hint 2

Check `callable(step)` for every step in `pipeline` itself (not inside the returned function),
so a bad step fails as soon as the pipeline is built.

## Hint 3

```
pipeline(*funcs):
    for step in funcs:
        if not callable(step): raise TypeError
    run(value):
        return reduce(lambda acc, step: step(acc), funcs, value)
    return run
```
