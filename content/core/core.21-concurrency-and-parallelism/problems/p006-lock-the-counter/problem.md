# Lock the counter

`starter.py` has a `Counter` class used by a web server to count requests from many threads:

```python
def increment(self):
    current = self._value
    time.sleep(0)            # stands for "other work" between the read and the write
    self._value = current + 1
```

`time.sleep(0)` sleeps for no time at all, but it **gives up the GIL**, so another thread runs
right in the gap between the read and the write. That makes the race happen on every run,
instead of once a week in production. With 8 threads doing 200 increments each, the starter
ends far below 1600.

Make `Counter` thread-safe:

- `Counter()` starts at 0.
- `increment()` adds 1. **Keep the three lines and the `time.sleep(0)`**; the tests check it is
  still there, because the gap is what proves your lock works.
- `value` is a read-only **property** that returns the current count.
- Use a `threading.Lock` (one per `Counter` object) so that read, gap and write happen as one
  step that no other thread can cut into.

**Example**

```python
import threading

c = Counter()

def work():
    for _ in range(200):
        c.increment()

threads = [threading.Thread(target=work) for _ in range(8)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print(c.value)
```

```text
1600
```

With the starter this prints a smaller number that changes from run to run (for example
`211`).
