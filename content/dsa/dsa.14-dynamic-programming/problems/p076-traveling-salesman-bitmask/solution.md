## Approach

Chapter section 19, plus parent pointers (chapter section 9).

- **State:** `f[mask][last]` = the shortest path from 0 that visits exactly the places in `mask` and ends at `last`.
- **Transition (push):** from a known `f[mask][last]`, go to an unvisited `nxt`: `f[mask | 1 << nxt][nxt] = min(..., f[mask][last] + dist[last][nxt])`, and remember `parent[...][nxt] = last`.
- **Base:** `f[1][0] = 0`.
- **Answer:** `min(f[full][last] + dist[last][0])` over `last` from 1 to `n - 1`. The drive back to 0 is not in `f`, so it is added here.
- **Order of filling:** `mask` upwards. A new state always has one more bit, so it is a bigger number, and it is reached before it is pushed from.

```python
INF = float("inf")


def shortest_tour(dist):
    n = len(dist)
    if n == 1:
        return 0, [0]
    full = (1 << n) - 1
    f = [[INF] * n for _ in range(1 << n)]       # f[mask][last]
    parent = [[None] * n for _ in range(1 << n)]
    f[1][0] = 0                                    # only place 0 visited, standing there
    for mask in range(1 << n):
        if not mask & 1:                           # every path starts at 0
            continue
        row = f[mask]
        for last in range(n):
            here = row[last]
            if here == INF:
                continue
            for nxt in range(n):
                if mask >> nxt & 1:                # already visited
                    continue
                new_mask = mask | (1 << nxt)
                cost = here + dist[last][nxt]
                if cost < f[new_mask][nxt]:
                    f[new_mask][nxt] = cost
                    parent[new_mask][nxt] = last
    length, last = min((f[full][last] + dist[last][0], last) for last in range(1, n))
    order, mask = [], full
    while last is not None:                        # walk back to place 0
        order.append(last)
        prev = parent[mask][last]
        mask &= ~(1 << last)
        last = prev
    order.reverse()
    return length, order
```

**The walk back.** `parent[mask][last]` is the place visited just before `last` on the best path for that state. Remove `last` from the mask and continue from the parent; place 0 has parent `None`, which stops the walk. For the first example the best final place is `last = 1` (`f[full][1] + dist[1][0] = 70 + 10`), and the walk is `1 ← 3 ← 2 ← 0`, reversed to `[0, 2, 3, 1]`: `15 + 30 + 25 + 10 = 80`. (Ending at place 2 also gives 80: the same tour driven the other way.)

**Why the state is enough.** Two different paths that visited the same set and stand at the same place have exactly the same choices from now on. Only the shorter one can be part of a best tour, so one number per `(mask, last)` is enough. This is the "overlapping sub-problems" idea with a set as part of the state.

## Complexity

`2**n * n` states, `n` choices each: `O(2**n * n**2)` time, `O(2**n * n)` memory. For `n = 13`: about 1.4 million steps, against 479 million orders for brute force.

## Another way

Pull instead of push: `f[mask][last] = min(f[mask without last][prev] + dist[prev][last])` over `prev` in the mask. It is the same table, filled by reading smaller masks. Without a `parent` table, the order can also be re-derived: at `(mask, last)`, find a `prev` with `f[mask without last][prev] + dist[prev][last] == f[mask][last]`.
