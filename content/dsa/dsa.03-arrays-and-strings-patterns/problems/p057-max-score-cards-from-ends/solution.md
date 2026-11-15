## Approach

Only the split matters: `x` cards from the left and `k - x` from the right, for some `x` from 0 to `k`. The cards
left on the table are then `a[x .. x + n - k - 1]`, a block of `n - k` consecutive cards, and every such block comes from
exactly one split. So the best score is the total minus the **smallest** block of length `n - k`: a fixed sliding
window. This is the "complement" trick: when the thing you choose is awkward (two pieces at the ends), look at what
you do not choose (one piece in the middle).

## Code

```python
n, k = [int(x) for x in input().split()]
a = [int(x) for x in input().split()]

total = sum(a)
keep = n - k

window = sum(a[:keep])
smallest = window
for i in range(keep, n):
    window += a[i] - a[i - keep]
    if window < smallest:
        smallest = window

print(total - smallest)
```

When `k = n`, `keep = 0`: the window is empty with sum 0, and `a[i] - a[i - 0]` adds 0 at every step, so the answer is
the total. No special case is needed.

## Complexity

O(n) time, O(1) extra memory.

## Another way

Try every split directly with two running sums: start with all `k` cards from the right; then move one card at a time
from the right group to the left group (`left += a[x - 1]`, `right -= a[n - k + x - 1]`), and keep the maximum of
`left + right`. Also O(n) (in fact O(k)). Recomputing each split with `sum()` is O(k) per split, O(k^2) in all: too slow
for `k = 100000`.

Greedy (always take the bigger end) is wrong: a small card can hide a huge one behind it.
