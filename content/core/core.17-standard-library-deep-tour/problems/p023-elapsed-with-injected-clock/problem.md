# Stopwatch and deadline with an injected clock

Code that measures time is hard to test: you do not want a test to `sleep(5)`, and real timings
are never exactly the same twice. The fix is to **inject the clock**: the class takes a function
that returns "the current time in seconds" and calls it instead of calling `time.perf_counter()`
directly. Real code uses the default; tests pass in a fake clock that they move by hand.

Write in `solution.py`:

1. `class Stopwatch(clock=time.perf_counter)`. Store the clock as `self.clock`.
   - `start()` begins a measurement (and clears old laps). Calling it while running raises `RuntimeError`.
   - `lap()` returns the seconds since the previous lap (or since `start()` for the first lap) and records it.
   - `stop()` returns the **total** seconds since `start()` and stops the stopwatch.
   - `lap()` or `stop()` when not running raise `RuntimeError`.
   - Property `laps`: a **copy** of the list of lap splits so far.

2. `class Deadline(seconds, clock=time.monotonic)`. Store the clock as `self.clock`. The deadline
   ends `seconds` after the moment it is created. Negative `seconds` raise `ValueError`.
   - `remaining()` returns the seconds left, never less than `0.0`.
   - `expired()` is `True` once the clock has reached the end time (at exactly the end, it is expired).

3. `timed(func, clock=time.perf_counter) -> tuple[result, seconds]`: call `func()` (no arguments)
   and return its result and how long it took. Read the clock exactly twice.

Why these defaults? `perf_counter` is the most precise clock for measuring short durations;
`monotonic` is guaranteed never to go backwards, which matters for deadlines and timeouts.
`time.time()` is the calendar clock: it can jump when the computer syncs its clock, so it is wrong for both jobs.

**Example** (with a fake clock that the test moves by hand)

```python
class FakeClock:
    def __init__(self): self.now = 1000.0
    def __call__(self): return self.now

clock = FakeClock()
sw = Stopwatch(clock)
sw.start()
clock.now += 1.0;  sw.lap()     # 1.0
clock.now += 3.0;  sw.lap()     # 3.0
clock.now += 0.5;  sw.stop()    # 4.5
sw.laps                          # [1.0, 3.0]
```
