## Hint 1

Draw a time line for each part. In part 1: at 0.01 `a` finishes, at 0.02 `b` raises. What does
`gather` do at 0.02, and is `c` cancelled? Then the main coroutine sleeps 0.05 more: where on
the time line does `c` (due at 0.03) land compared to `gather over`?

## Hint 2

In part 3, at 0.02 `h` raises inside the group. The group cancels every task that has not
finished: which ones are those? A cancelled task runs its `except asyncio.CancelledError`
block. Does the line `print("after the block")` run when the block raised? What is the type
name of the group that `except*` receives?

```
part 1: 0.01 a done | 0.02 b fails -> gather raises, c keeps going | 0.03 c done | 0.07 over
part 2: d done, f done, then the list with the exception object in slot 2
part 3: 0.01 g done | 0.02 h fails -> cancel i -> "i cancelled" -> ExceptionGroup(['h'])
```
