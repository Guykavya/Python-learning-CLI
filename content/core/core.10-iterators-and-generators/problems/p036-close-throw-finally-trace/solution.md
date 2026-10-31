## Approach

Follow the pause point step by step.

1. `worker()` only creates the generator. Nothing prints, so `made` comes first.
2. `next(w)` runs the body: `open`, enter both `try` blocks, pause at `yield`.
3. `w.send("a")`: `job = "a"`, print `job a`, loop, pause again.
4. `w.throw(ValueError("oops"))`: the paused `yield` raises `ValueError`. The inner `except` prints
   `bad job: oops`. The loop goes round to the `yield`, which yields `None`. `throw` returns that
   value, so the outer `print` prints `None`.
5. `w.send("b")`: `job b`.
6. `w.close()`: `GeneratorExit` is raised at the `yield`. It is not a `ValueError`, so it passes
   the inner `except`, and the `finally` prints `cleanup`. The generator is now finished.
   `close()` swallows the `GeneratorExit`, so the program goes on and prints `closed`.
7. A second `close()` on a finished generator does nothing.
8. `send("c")` on a finished generator raises `StopIteration`: `dead`.
9. `w2` never started. Its body never ran, so it never entered the `try`. `close()` just marks it
   finished: no `open`, no `cleanup`. Then `never started`.

## Output

```text
made
open
job a
bad job: oops
None
job b
cleanup
closed
dead
never started
```

## Complexity

O(1): a fixed number of steps.

## Another way

Put `print("paused")` just before `job = yield` and run it. You will see one `paused` for each
`next`, `send` and caught `throw`, which shows that `throw` also resumes the generator to its next `yield`.
This is why `try/finally` in a generator is a good place for cleanup: it runs when the
generator ends normally, when it fails, and when the user calls `close()` early.
