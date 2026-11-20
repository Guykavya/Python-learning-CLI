## Hint 1

Ask two questions for each situation. (a) Is the same expensive **read** repeated many times, and is a slightly old answer acceptable? Then a cache helps. (b) Is there slow or unreliable **work** that the user does not need to wait for? Then a queue helps.

## Hint 2

If both answers are yes, write `both`. If the answer must be exact at this very moment (money, one-time use) and the work is quick, write `neither`: a stale cached answer would be a real bug.

```text
for each situation:
    cache_ok = repeated read and staleness acceptable
    queue_ok = slow work the user need not wait for
    both / cache / queue / neither from those two booleans
```
