- Printing `P: cancelled, cleaning up` right after `cancel P: True`. `cancel()` only
  requests; P runs its handler later, when `main` pauses at `await gather`.
- `P done right after cancel? True`. P has not run since the request, so it is not done.
- Printing `P: finished`. The `CancelledError` replaces the rest of the `try` body.
- Forgetting `P: finally` or printing it before the `except` line. On the way out, the
  matching `except` runs first, then `finally`.
- `results: ['CancelledError', 'CancelledError']`. S swallowed its cancel and returned
  `"S result"`.
- `S cancelled? True`. A task is "cancelled" only if the `CancelledError` escaped it.
- `cancel P again: True`. A finished task cannot be cancelled.
- Printing `after slow`, or `main: TimeoutError ...` before `slow: finally`. The cancel
  travels up through `slow`'s `finally` first, and only becomes `TimeoutError` at the end of
  the `async with` block.
- Thinking `wait_for` just stops waiting and leaves `W` running. It cancels `W`, so W's
  handler and `finally` print before the `TimeoutError` reaches `main`.
