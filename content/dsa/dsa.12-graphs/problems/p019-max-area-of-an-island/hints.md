## Hint 1

p018 found each island with one search. Now each search must also **count** the cells it reaches. When exactly do you add 1: when a cell is pushed, or when it is popped? Can the same cell be counted twice?

## Hint 2

```
best = 0
for every unseen land cell (r, c):
    seen[r][c] = True; stack = [(r, c)]; area = 0
    while stack:
        pop a cell; area += 1
        for each land neighbour not seen: mark it, push it
    best = max(best, area)
return best
```

Because a cell is marked when it is pushed, it is pushed once, so it is popped (and counted) once.
