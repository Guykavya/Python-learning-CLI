## Hint 1

The exception happens **inside the thread**, in the function the thread runs. Which code runs
in that thread and could catch it there? What should that code store in the result slot when
it catches something?

## Hint 2

Put the `try` inside the target, around the call:

```
define call(index, func):
    try:
        results[index] = ("ok", func())
    except Exception as exc:
        results[index] = ("error", exc)
```

Then start all threads and join all, exactly like p002. Why `Exception` and not a bare
`except:`?
