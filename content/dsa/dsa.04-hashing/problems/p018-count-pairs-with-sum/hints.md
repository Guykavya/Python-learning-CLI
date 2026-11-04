## Hint 1

When you reach position `j`, how many earlier positions `i` would make a valid pair with it? Which table tells you?

## Hint 2

Keep `seen[v]` = how many times `v` has appeared so far. At each `x`, add `seen.get(k - x, 0)` to the answer, **then** add `x` to the table.

## Hint 3

```
ans = 0
for x in a:
    ans += seen.get(k - x, 0)
    seen[x] = seen.get(x, 0) + 1
```
