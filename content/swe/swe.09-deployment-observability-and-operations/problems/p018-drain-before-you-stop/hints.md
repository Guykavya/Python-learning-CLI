## Hint 1

`track` is a context manager: which decorator from `contextlib` turns a generator with one `yield` into one? What must always happen after the `yield`, even when the request raises? And since several threads change the same counter, what protects `in_flight += 1`?

## Hint 2

```text
track:  with lock: in_flight += 1
        try: yield
        finally: with lock: in_flight -= 1
wait_idle(timeout, poll):
    deadline = clock() + timeout
    while in_flight > 0:
        remaining = deadline - clock()
        if remaining <= 0: return False
        sleep(min(poll, remaining))
    return True
```
