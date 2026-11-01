## Approach

Follow the one thread through the program. There is only one task (`main`), so every
`await` simply runs the awaited coroutine to its end before the next line.

| Step | Line | What happens | Printed |
|---|---|---|---|
| 1 | `print("before run")` | the two `def`s only defined functions | `before run` |
| 2 | `coro = main()` | creates a coroutine object; `main`'s body does **not** run | |
| 3 | `print(..., type(coro).__name__)` | the type is `coroutine` | `main() gave a coroutine` |
| 4 | `asyncio.run(coro)` | starts a loop and runs `main`'s body | `main start` |
| 5 | `c = greet("A")` | another coroutine object, body not run | |
| 6 | `print("made", ...)` | | `made coroutine` |
| 7 | `await c` | greet A runs; `sleep(0)` pauses it, but nothing else is ready, so it resumes at once | `greet start A`, `greet end A` |
| 8 | `print("result:", result)` | `await` gave the return value | `result: hi A` |
| 9 | `await greet("B")` | B runs to the end | `greet start B`, `greet end B` |
| 10 | `await greet("C")` | only now does C start | `greet start C`, `greet end C` |
| 11 | prints in `main` | | `hi B \| hi C`, `main end` |
| 12 | `asyncio.run` returns `main`'s return value | | `run returned 42` |

The key lesson is step 9 to 10: **two `await`s in a row run one after the other**. Writing
`async` does not make code concurrent. To overlap B and C you need tasks (`create_task`) or
`asyncio.gather(greet("B"), greet("C"))`.

## Output

```text
before run
main() gave a coroutine
main start
made coroutine
greet start A
greet end A
result: hi A
greet start B
greet end B
greet start C
greet end C
hi B | hi C
main end
run returned 42
```

## Complexity

Not relevant for a trace.

## Another way

Replace steps 9 and 10 with `r1, r2 = await asyncio.gather(greet("B"), greet("C"))` and trace
it again: now both start before either ends (`greet start B`, `greet start C`, `greet end B`,
`greet end C`), because `sleep(0)` lets the other task run.
