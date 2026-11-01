- `t.start(); t.join()` in the same loop. Each thread finishes before the next one starts, so
  nothing overlaps.
- `Thread(target=func(*args))`. That **calls** `func` right now, in the main thread, and passes
  its return value as the target. Pass the function and its arguments separately.
- `args=(x)` for one argument. `(x)` is not a tuple; write `(x,)`.
- Appending results with `results.append(...)` from each thread. The list ends up in
  **finish** order, not input order.
- Calling `t.run()` instead of `t.start()`. `run()` executes the target in the **current**
  thread, so nothing is concurrent.
- Returning before joining. The threads may not have written their results yet.
