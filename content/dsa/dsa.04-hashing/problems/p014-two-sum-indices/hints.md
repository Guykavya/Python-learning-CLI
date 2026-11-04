## Hint 1

For a fixed `x`, which other value would complete the pair? Where could you look it up in O(1)?

## Hint 2

Walk left to right with `seen` mapping value to index. For each `x` at index `j`, check `target - x in seen` **before** storing `x`.

## Hint 3

```
seen = {}
for j, x in enumerate(a):
    need = target - x
    if need in seen: print(seen[need], j); stop
    seen[x] = j
```
