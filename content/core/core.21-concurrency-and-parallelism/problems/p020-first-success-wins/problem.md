# First success wins

Your app can read the same data from three mirrors. Some mirrors are slow, some are down.
You want to ask **all of them at once** and use the **first good answer**, without waiting
for the slow ones to finish.

Write `first_success(funcs, timeout)` in `solution.py`:

- `funcs` is a list of functions that take no arguments (one per mirror). Run each one in
  its own thread with a `ThreadPoolExecutor` (one worker per function).
- Return the value of the **first function that returns normally**. Functions that raise are
  skipped: keep waiting for the others.
- Return **as soon as** a good value is there. Do not wait for the slower functions to finish
  (they keep running in the background; Python cannot stop a thread). Cancel the futures you
  no longer need, so that any job that has not started yet never starts.
- If **every** function raises, raise `RuntimeError` whose message contains how many failed,
  for example `"all 3 functions failed"`, chained from the last error
  (`raise RuntimeError(...) from err`).
- If no function has succeeded after `timeout` seconds in total (counted from the call),
  raise the built-in `TimeoutError`.
- An empty `funcs` raises `ValueError`.

Use `concurrent.futures.wait(..., return_when=FIRST_COMPLETED)` in a loop.

**Example**

```python
import time

def mirror(value, seconds, fail=False):
    def run():
        time.sleep(seconds)
        if fail:
            raise ConnectionError(f"{value} is down")
        return value
    return run

first_success([mirror("A", 0.5), mirror("B", 0.1, fail=True), mirror("C", 0.2)], timeout=2)
# 'C'   after about 0.2 s: B failed first and was skipped, A was not waited for

first_success([mirror("A", 0.1, fail=True), mirror("B", 0.1, fail=True)], timeout=2)
# RuntimeError: all 2 functions failed

first_success([mirror("A", 1.0)], timeout=0.2)
# TimeoutError   after about 0.2 s
```
