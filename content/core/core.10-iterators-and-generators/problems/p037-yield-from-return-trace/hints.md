## Hint 1

Who receives each `send`? While `outer` is inside `yield from inner("A")`, `outer` itself is
frozen. Every `send` goes to `inner("A")`, and every value `inner("A")` yields goes straight back
to the caller. Write down, after each line of the main program, which generator is running and
where it is paused.

## Hint 2

`next(g)` sends `None`. In `inner`, `x is None` means `break`. After the loop `inner` prints
`ends` and returns `total`. That return value becomes `a` (or `b`) in `outer`. Then `outer`
continues **in the same call** until it reaches its next `yield`. Which `yield` is that?

## Hint 3

Use a table:

```
call         who runs           prints                     value given back
next(g)      inner A starts     "A starts"                 0
send(5)      inner A            "A got 5"                  5
send(3)      ...
next(g)      inner A ends, outer continues, inner B starts ...
```

The last `next(g)` makes `outer` run past its last `yield` to `return "ok"`.
