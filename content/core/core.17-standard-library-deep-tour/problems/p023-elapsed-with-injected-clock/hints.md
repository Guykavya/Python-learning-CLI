## Hint 1

A clock is just "a function with no arguments that returns a float". `time.perf_counter` (without
brackets) is such a function, and so is the test's `FakeClock()` object. Store it, then always
call `self.clock()`. What must you remember at `start()` so that `stop()` and `lap()` can compute a difference?

## Hint 2

You need three pieces of state: the start reading (or `None` when not running), the reading at the
last lap, and the list of laps. `Deadline` only needs one number: `clock() + seconds`, computed in `__init__`.

## Hint 3

```
start:     if running: raise RuntimeError
           start = last = clock();  laps = []
lap:       if not running: raise RuntimeError
           now = clock(); split = now - last; last = now; laps.append(split); return split
stop:      if not running: raise RuntimeError
           total = clock() - start; start = None; return total
Deadline:  end = clock() + seconds
           remaining = max(0.0, end - clock());  expired = clock() >= end
timed:     t0 = clock(); r = func(); return r, clock() - t0
```
