## Hint 1

If you know `x` is in the set, how can you test in O(1) whether `x + 1` is also there?

## Hint 2

Counting from every value repeats work: from `3` you count 3,4,5 and from `4` again 4,5. Only start from values with no `x - 1` neighbour.

## Hint 3

```
values = set(a)
best = 0
for x in values:
    if x - 1 not in values:
        length = 1
        while x + length in values: length += 1
        best = max(best, length)
```
