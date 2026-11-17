## Approach

The chapter's `open_lock` with the length taken from `target`. Dead ends behave like walls: they are never entered. The start is checked first, because BFS would otherwise happily begin inside a dead state.

## Code

```python
from collections import deque


def open_lock(deadends, target):
    k = len(target)
    dead = set(deadends)
    start = "0" * k
    if start in dead:
        return -1
    dist = {start: 0}
    queue = deque([start])
    while queue:
        state = queue.popleft()
        if state == target:
            return dist[state]
        for i in range(k):
            digit = int(state[i])
            for step in (1, -1):
                nxt = state[:i] + str((digit + step) % 10) + state[i + 1:]
                if nxt not in dead and nxt not in dist:
                    dist[nxt] = dist[state] + 1
                    queue.append(nxt)
    return -1
```

## Complexity

At most `10**k` states, each with `2k` neighbours of length `k`: `O(10**k * k^2)` with string slicing, `O(10**k)` memory.

## Another way

Bidirectional BFS from `start` and `target` at the same time. Without dead ends the answer is a formula: the sum over the wheels of `min(d, 10 - d)`. Dead ends are what make a search necessary.
