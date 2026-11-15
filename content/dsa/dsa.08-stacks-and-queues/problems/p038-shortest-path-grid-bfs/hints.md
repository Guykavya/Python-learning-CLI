## Hint 1

Put `(row, col, steps)` into the queue, starting with `(start_row, start_col, 0)`, and keep a set `seen = {start}`. When you take a cell out: if it is the goal, return its steps. Otherwise, which neighbours do you add, and when do you put them into `seen`?

## Hint 2

```
queue = deque([(r0, c0, 0)]); seen = {start}
while queue:
    r, c, steps = queue.popleft()
    if (r, c) == goal: return steps
    for dr, dc in the 4 directions:
        nr, nc = r + dr, c + dc
        if inside and grid[nr][nc] != "#" and (nr, nc) not in seen:
            seen.add((nr, nc))          # mark NOW, when enqueued
            queue.append((nr, nc, steps + 1))
return -1
```

Check the walls at `start` and `goal` before the loop.
