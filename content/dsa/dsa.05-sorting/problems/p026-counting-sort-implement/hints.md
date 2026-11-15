## Hint 1

If you knew that value 7 occurs 3 times, where would the three 7s have to go in the sorted output? What do you need to know about the smaller values?

## Hint 2

Make `count = [0] * (k + 1)`, do `count[x] += 1` for every value, then for `v` in `range(k + 1)` output `v` repeated `count[v]` times.

## Hint 3

```
count = [0] * (k + 1)
for x in a: count[x] += 1
out = []
for v in range(k + 1): out.extend([v] * count[v])
```
