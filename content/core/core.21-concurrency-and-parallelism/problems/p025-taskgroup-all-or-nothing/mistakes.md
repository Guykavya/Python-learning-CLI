- Using `gather`. The first error is raised while the other loaders keep running (and
  using connections) in the background.
- Wrapping the `async with` in `try/except Exception`. An `ExceptionGroup` *is* an
  `Exception`, so this swallows every failure; the task says to let it propagate.
- Expecting a plain `ValueError` from the group. A `TaskGroup` always raises an
  `ExceptionGroup`, even for one error; catch it with `except* ValueError`.
- Reading `task.result()` **inside** the `async with` block. The tasks are not finished yet,
  so `result()` raises `InvalidStateError`.
- Writing `tg.create_task(loader)` (the function) instead of `tg.create_task(loader())` (a
  coroutine). `create_task` needs a coroutine.
- Catching `CancelledError` in a loader and not re-raising it. The group then cannot finish
  cancelling cleanly and the loader's "result" is wrong.
