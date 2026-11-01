# Stop a worker with an Event

Python has no safe way to "kill" a thread from outside. Instead, the thread checks a flag and
stops itself. A `threading.Event` is the right flag: `stop.set()` from any thread, and
`stop.is_set()` or `stop.wait(...)` in the worker.

Write `worker(stop, tick, interval)`:

- `stop` is a `threading.Event`, `tick` is a function with no arguments, `interval` is a
  number of seconds.
- If `stop` is already set, return `0` at once without calling `tick`.
- Otherwise call `tick()`, then wait `interval` seconds, then call `tick()` again, and so on,
  until `stop` is set.
- Return how many times `tick()` was called.
- **Stop promptly.** If `stop` is set in the middle of a 10-second wait, the worker must return
  within a fraction of a second, not after the 10 seconds. That is why you must wait with
  `stop.wait(interval)` and not with `time.sleep(interval)`: `stop.wait` returns **as soon as**
  the event is set (it returns `True`), or after the timeout (it returns `False`).

**Example**

```python
import threading, time

stop = threading.Event()
counts = []
t = threading.Thread(target=lambda: counts.append(worker(stop, lambda: print("tick"), 1.0)))
t.start()
time.sleep(2.5)
stop.set()
start = time.perf_counter()
t.join()
print(counts, f"stopped after {time.perf_counter() - start:.2f} s")
```

```text
tick
tick
tick
[3] stopped after 0.00 s
```

(Ticks at 0 s, 1 s and 2 s; `set()` at 2.5 s ends the wait at once. Your stop time will be a
tiny number.)
