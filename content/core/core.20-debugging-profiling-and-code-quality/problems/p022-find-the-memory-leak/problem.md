# Find the memory leak

Python frees an object as soon as nothing refers to it any more. So a "memory leak" in Python
almost always means: **something long-lived keeps a reference it should have let go of**. The
usual suspects are a module-level cache that only grows, and a list of listeners (callbacks)
that objects add themselves to but never leave.

`starter.py` is a module from a server that runs for weeks. Every function gives the right
answers, but memory grows without limit. A `tracemalloc` snapshot comparison after an hour of
traffic pointed at two lines (the numbers are made up for this exercise, the shape is real):

```text
starter.py:17: size=38.1 MiB (+38.1 MiB), count=412907 (+412907), average=97 B
starter.py:33: size=21.4 MiB (+21.4 MiB), count=120004 (+120004), average=187 B
```

Copy `starter.py` to `solution.py`, find both leaks and fix them **without changing the
behaviour** the rest of the program relies on:

1. **The cache.** `parse_record` must keep at most `MAX_CACHE` (1000) lines. When it is full and
   a new line arrives, drop the **least recently used** line (a line counts as "used" when it is
   stored or answered from the cache). `cache_size()` returns the number of cached lines,
   `clear_cache()` empties the cache and sets `stats["computed"]` back to 0, and
   `stats["computed"]` still counts how many times a record was really parsed (cache misses).
2. **The listeners.** `EventBus.unsubscribe(handler)` must remove the handler (doing nothing if
   it is not there). `Widget.close()` must unsubscribe the widget so the bus no longer holds it;
   calling `close()` twice is allowed. A closed widget no longer receives events, and once the
   program drops its own reference, the widget can be garbage collected.
3. A handler may close its own widget **while** `publish` is running. Every other handler that
   was subscribed when `publish` started must still receive that event.

**Example**

```python
for i in range(5000):
    parse_record(f"user{i}, {i % 90}, Pune")
cache_size()            # 1000, not 5000

bus = EventBus()
for _ in range(10_000):
    Widget(bus).close()
bus.handler_count()     # 0, not 10000
```
