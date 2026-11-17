## Hint 1

Which courses can be taken in semester 1? After they are done, which courses become possible? Kahn's algorithm takes vertices one at a time; how can you make it take them one **round** at a time and count the rounds?

## Hint 2

Start `ready` with every course of in-degree 0. While `ready` is not empty: count one more round, and process **exactly** the courses that are in `ready` at the start of the round (`for _ in range(len(ready))`), lowering in-degrees and appending newly freed courses for the next round. Count the courses you took; if it is less than `n`, return `-1`.

## Hint 3

```
ready = deque(v for v in range(n) if indeg[v] == 0)
rounds = done = 0
while ready:
    rounds += 1
    for _ in range(len(ready)):
        u = ready.popleft(); done += 1
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0: ready.append(v)
return rounds if done == n else -1
```
