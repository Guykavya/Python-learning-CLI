## Hint 1

Count the wasted calls: with candidates `[2, 89]` and remaining 3, the starter calls `go` for 89 and only then sees the negative remainder. What could the loop check **before** `path.append`?

## Hint 2

If you check `candidates[i] > remaining` in the loop, you can use `continue`. If the candidates are **sorted**, you can use `break`: every later candidate is even bigger. With the check in the loop, the `remaining < 0` test at the top is no longer needed.

## Hint 3

```
candidates = sorted(candidates)
...
for i in range(start, len(candidates)):
    if candidates[i] > remaining: break
    path.append(candidates[i]); go(i, remaining - candidates[i]); path.pop()
```
