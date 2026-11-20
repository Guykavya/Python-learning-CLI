## Hint 1

Draw a small grid for `a = [1, 7, 11]` and `b = [2, 4, 6]` and write the sums in it. Where is the smallest sum? After you took it, which cells could be the second smallest? Compare with merging `len(a)` sorted lists (the rows of the grid), stopped after `k` numbers.

## Hint 2

Start the heap with the first cell of each of the first `min(k, len(a))` rows: `(a[i] + b[0], i, 0)`. Rows after the `k`-th cannot contribute: the cell `(k, 0)` already has `k` cells above it with smaller or equal sums. Pop the smallest cell `(sum, i, j)`, output the pair `(a[i], b[j])` and push the right neighbour `(a[i] + b[j + 1], i, j + 1)`, if there is one.

## Hint 3

```
if a is empty or b is empty or k <= 0: return []
heap = [(a[i] + b[0], i, 0) for i in range(min(k, len(a)))]
heapify(heap)
result = []
while heap and len(result) < k:
    s, i, j = pop(heap)
    result.append((a[i], b[j]))
    if j + 1 < len(b): push(heap, (a[i] + b[j + 1], i, j + 1))
return result
```
