## Hint 1

The neighbours of a state: for each wheel `i`, the digit `d` becomes `(d + 1) % 10` or `(d - 1) % 10`. That is `2k` neighbours. Which container makes "is this state dead?" fast? And where do you check the start?

## Hint 2

```
dead = set(deadends); start = "0" * len(target)
if start in dead: return -1
dist = {start: 0}; queue = deque([start])
while queue:
    s = popleft; if s == target: return dist[s]
    for i in range(k): for step in (1, -1):
        nxt = s[:i] + str((int(s[i]) + step) % 10) + s[i+1:]
        if nxt not in dead and nxt not in dist: dist[nxt] = dist[s] + 1; append
return -1
```
