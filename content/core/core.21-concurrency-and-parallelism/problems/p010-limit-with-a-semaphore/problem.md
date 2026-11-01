# Limit how many run at once with a Semaphore

A script downloads files from a server that allows only **3 connections per client**. You
want one thread per file (it keeps the code simple), but at most 3 of them may be
**inside** the download at the same time.

A `threading.Semaphore(n)` is a counter of free places. `acquire()` takes a place, waiting
if none is free; `release()` gives it back. Used as `with sem:` it does both for you.

Write `run_limited(funcs, limit)`:

- `funcs` is a list of functions with no arguments.
- Start **one thread per function**, all at once.
- At most `limit` of the functions may be **running** at any moment. The others wait
  (inside their threads) until a place is free.
- Return the list of return values **in input order**.
- If a function raises, its slot stays `None` (the thread prints the traceback), but its place
  must still be given back so the other functions can run.

`starter.py` already runs every function in its own thread and keeps the order, but it has no
limit at all.

**Example**

```python
import threading, time

running = 0
peak = 0
lock = threading.Lock()

def download():
    global running, peak
    with lock:
        running += 1
        peak = max(peak, running)
    time.sleep(0.1)
    with lock:
        running -= 1
    return "done"

print(run_limited([download] * 7, limit=3))
print("peak:", peak)
```

```text
['done', 'done', 'done', 'done', 'done', 'done', 'done']
peak: 3
```

With the starter the peak is 7.
