## Hint 1

Offline sweep. Sort the positions by their mark, and the questions by `x`. Go through the questions in increasing `x`; before answering one, insert (`add(pos, 1)` in a Fenwick tree over positions) every mark that is **strictly less** than its `x`. Then the answer is the number of inserted positions in `[l, r)`: a range sum.

## Hint 2

Keep a pointer into the sorted marks; it only moves forward, so all insertions together cost `O(n log n)`. Store each answer at the question's original index.

## Hint 3

```
order = positions sorted by a[pos]
bit = Fenwick(n); j = 0; ans = [0] * q
for qi in questions sorted by x:
    l, r, x = queries[qi]
    while j < n and a[order[j]] < x: bit.add(order[j], 1); j += 1
    ans[qi] = bit.range_sum(l, r)
```
