## Hint 1

Start with the shell: read everything with `sys.stdin.read().split()`; the first token is the letter. Then write three functions, one per letter. Do the problems in order A, B, C and test each.

## Hint 2

A: a deletion is needed for every position equal to the previous one. B: walk through the array with a counter dictionary: for each `x`, add `count[k - x]`, then count `x`. C: flatten the grid, and use an explicit stack to mark the cells of an island as visited.

## Hint 3

```text
A: sum over s of (s[i] == s[i-1]) for i >= 1
B: cnt = {}; for x in a: ans += cnt.get(k - x, 0); cnt[x] = cnt.get(x, 0) + 1
C: for each unvisited '#': islands += 1, stack = [cell]; while stack: pop cell, push unvisited '#' neighbours
```
