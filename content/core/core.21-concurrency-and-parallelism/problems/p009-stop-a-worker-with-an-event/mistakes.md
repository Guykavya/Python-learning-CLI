- Using `time.sleep(interval)` and checking `stop.is_set()` around it. The stop request is
  only seen after the sleep ends: up to a full interval late.
- Using a plain global `running = False` flag with `time.sleep`. Same delay, and a bool cannot
  wake a sleeping thread. An `Event` can.
- Busy-waiting: `while not stop.is_set(): pass` or sleeping 0.001 s in a loop to check the
  time. It burns CPU for nothing.
- Ignoring the return value of `stop.wait(...)` and ticking once more after `set()`.
- Making the worker a non-daemon thread and never setting `stop`. The program cannot exit,
  because Python waits for non-daemon threads at the end.
