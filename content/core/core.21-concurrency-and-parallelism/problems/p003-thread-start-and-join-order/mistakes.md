- Expecting `B runs in worker-B`. `run()` is a normal method call, so the target runs in the
  thread that called it: `MainThread`.
- Writing `after b.run(), alive: True`. A thread is alive only between `start()` and the end of
  its target; `b` was never started.
- Writing `main: C alive? False` at step 9. C is blocked in `go.wait()`, but blocked is not
  finished.
- Putting `C: finished` before `main: keeps going while C waits`. C cannot finish until main
  calls `go.set()`, which comes after that print.
- Thinking `d.join()` returns the value. `join()` always returns `None`; the result comes
  through the shared `results` list.
