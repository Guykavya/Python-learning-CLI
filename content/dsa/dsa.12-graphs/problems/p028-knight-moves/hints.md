## Hint 1

What are the vertices and what are the edges? Write the list of the 8 moves `(dr, dc)` once. From a square, which of the 8 targets are allowed? When can you stop the search?

## Hint 2

BFS from `start` with a queue of `(square, distance)` and a `seen` set. Before pushing a square, check that it is on the board and not seen; mark it when you push it. Return the distance as soon as you pop (or push) `target`. If the queue runs empty, return `-1`.

## Hint 3

```
if start == target: return 0
moves = [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]
seen = {start}; queue = deque([(start, 0)])
while queue:
    (r, c), d = queue.popleft()
    for dr, dc in moves:
        nxt = (r + dr, c + dc)
        if 0 <= nxt[0] < n and 0 <= nxt[1] < n and nxt not in seen:
            if nxt == target: return d + 1
            seen.add(nxt); queue.append((nxt, d + 1))
return -1
```
