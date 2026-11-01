## Hint 1

All threads may be **started** at once; the limit is about how many are **inside** their
function. So where must the waiting happen: in the main thread before `start()`, or inside
each thread before it calls `func()`? How many semaphores do you need for the whole call?

## Hint 2

```
places = BoundedSemaphore(limit)        # one, shared by every thread

define call(index, func):
    with places:                         # waits here if `limit` threads are inside
        results[index] = func()          # place is returned even if func raises

start all threads, join all, return results
```
