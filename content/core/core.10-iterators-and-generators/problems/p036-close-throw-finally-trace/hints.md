## Hint 1

Mark the place where `w` is paused after each line. `next(w)` runs until the first `yield`.
`send("a")` resumes there: what does `job` become, and where does the generator pause next?

## Hint 2

`throw(ValueError(...))` raises the error **at the paused `yield`**. The inner `except ValueError`
catches it, prints, and the loop goes round to the `yield` again. Like `send`, `throw` returns the
next value the generator yields. A bare `yield` yields `None`.

## Hint 3

`close()` raises `GeneratorExit` at the paused `yield`. `GeneratorExit` is **not** a `ValueError`,
so the inner `except` ignores it. It travels out through the `finally`. Think:

```
close -> GeneratorExit at yield -> except ValueError? no -> finally runs -> generator is finished
```

A generator that never started has not entered the `try` yet. What can its `finally` do then?
