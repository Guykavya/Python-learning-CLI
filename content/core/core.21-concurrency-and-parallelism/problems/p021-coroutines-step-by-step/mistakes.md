- Printing `main start` right after `before run`. `main()` only creates the coroutine; the
  body starts inside `asyncio.run`.
- Printing `greet start A` before `made coroutine`. Calling `greet("A")` runs nothing.
- Writing `made function` or `made greet`. The object is a `coroutine`.
- Interleaving B and C (`greet start B`, `greet start C`, ...). Plain sequential `await`s do
  not overlap; there are no tasks here.
- Thinking `await asyncio.sleep(0)` lets `main` continue before `greet` ends. `main` is the
  one waiting for `greet`; it cannot move on until `greet` returns.
- Writing `run returned None`. `asyncio.run` returns what `main` returned: `42`.
