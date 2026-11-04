## Approach

A window that must have **exactly** `k` distinct values has no clear "grow or shrink" rule: for `[1, 2, 1, 2]` and
`k = 2`, the windows `[1, 2]`, `[2, 1, 2]` and `[1, 2, 1, 2]` all qualify and end in different places. "At most `m`"
does have a rule: shrink while there are more than `m` distinct values. And once `a[left..right]` is the longest good
window ending at `right`, the good subarrays ending at `right` are exactly the `right - left + 1` suffixes of it.

The subarrays with at most `k` distinct values split into those with exactly `k` and those with at most `k - 1`, so
`exactly(k) = atMost(k) - atMost(k - 1)`.

## Code

```python
n, k = [int(x) for x in input().split()]
a = [int(x) for x in input().split()]


def at_most(m):
    count = {}
    left = 0
    total = 0
    for right in range(len(a)):
        x = a[right]
        count[x] = count.get(x, 0) + 1
        while len(count) > m:
            y = a[left]
            count[y] -= 1
            if count[y] == 0:
                del count[y]
            left += 1
        total += right - left + 1
    return total


print(at_most(k) - at_most(k - 1))
```

For the example `1 2 1 2 3`, `k = 2`: `atMost(2) = 1 + 2 + 3 + 4 + 2 = 12`, `atMost(1) = 5` (only single
elements), and `12 - 5 = 7`.

## Complexity

Two passes, each O(n): `left` and `right` each move at most `n` times. The dictionary holds at most `k + 1` keys.

## Another way

One pass with **two** left pointers. `l1` is the first start such that `a[l1..right]` has at most `k` distinct
values, and `l2` is the first start such that `a[l2..right]` has at most `k - 1`. The starts `l1, ..., l2 - 1` give
exactly `k` distinct values, so add `l2 - l1` at each step. It is the same idea with both windows running side by
side.

A brute force (`for i`, then `for j` with a set) is O(n^2) when values repeat a lot: for 200000 equal values it
checks 2 * 10^10 pairs.
