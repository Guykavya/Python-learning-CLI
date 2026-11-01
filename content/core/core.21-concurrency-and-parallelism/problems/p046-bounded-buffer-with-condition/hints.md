## Hint 1

For each method, what condition must be true before it may act? `put` needs room
(`len < capacity`), `get` needs an item (`len > 0`). While it is false the thread must sleep
**without holding the lock** (otherwise nobody else could change the state). Which Condition
method sleeps, releases the lock while sleeping, and re-checks a predicate every time it is
woken?

## Hint 2

After a `put`, who might be waiting for this change? After a `get`? Both kinds of waiters sleep
on the **same** Condition, so wake them all and let each re-check its own predicate.

```
put(item, timeout):
    with cond:
        if not cond.wait_for(lambda: len(items) < capacity, timeout):
            raise TimeoutError
        items.append(item)
        cond.notify_all()

get(timeout):
    with cond:
        if not cond.wait_for(lambda: len(items) > 0, timeout):
            raise TimeoutError
        item = items.popleft()
        cond.notify_all()
        return item
```
