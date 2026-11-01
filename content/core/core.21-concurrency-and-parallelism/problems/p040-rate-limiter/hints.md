## Hint 1

Keep the **times of recent starts** in a `deque` (oldest on the left). When someone wants to
start at time `now`, which starts no longer count? After dropping them, how many are left, and
if the window is full, how long until the oldest one drops out?

## Hint 2

Why might several waiting tasks all wake up and all start together? What if only **one** task
at a time were allowed to do "check the window, maybe sleep, record the start"? Which asyncio
object lets tasks through one at a time, in the order they arrived?

## Hint 3

```
async def __aenter__(self):
    async with self._lock:                       # created in __init__
        while True:
            now = self.clock()
            while starts and starts[0] + per <= now:
                starts.popleft()
            if len(starts) < rate:
                starts.append(now)
                return self
            await self.sleep(starts[0] + per - now)

async def __aexit__(self, exc_type, exc, tb):
    return False
```
