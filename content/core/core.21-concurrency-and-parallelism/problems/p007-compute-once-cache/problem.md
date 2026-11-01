# A cache that computes each key only once

A web service loads user profiles from a slow database. Many requests (threads) ask for the
same user at the same moment. A plain dictionary cache has a **check-then-act** race: ten
threads all see "not in cache", and all ten run the slow query.

Write a class `OnceCache` with one method:

```python
cache.get(key, compute)
```

- `compute` is a function with **no arguments** that produces the value for `key`
  (it may be slow).
- If `key` is already cached, return the cached value without calling `compute`.
- If several threads call `get` with the **same** key at the same time, `compute` must run
  **exactly once**; the other threads wait and then return the same value.
- Calls for **different** keys must not wait for each other: their `compute` calls run in
  parallel. (So one big lock around everything is not enough.)
- If `compute` raises, the exception goes to that caller and **nothing is cached**, so a later
  `get` for that key tries again.

**Example**

```python
import threading, time

calls = 0

def load_user():
    global calls
    calls += 1
    time.sleep(0.1)          # slow database
    return {"name": "Asha"}

cache = OnceCache()
results = []
threads = [threading.Thread(target=lambda: results.append(cache.get("u1", load_user)))
           for _ in range(8)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print(calls, len(results), all(r is results[0] for r in results))
```

```text
1 8 True
```

`starter.py` is the plain dictionary version: it prints `8 8 False` here.
