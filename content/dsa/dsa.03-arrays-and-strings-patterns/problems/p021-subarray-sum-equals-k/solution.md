## Approach

The sum of `a[i..j]` equals `P[j+1] - P[i]`, where `P` is the prefix-sum array with `P[0] = 0`. That sum is `k`
exactly when `P[i] = P[j+1] - k`. So for every end position we need to know **how many** earlier prefixes have
the value `P[j+1] - k`. Keep those counts in a dictionary while you walk the array once.

The dictionary starts as `{0: 1}`: the empty prefix before the array. Without it, subarrays that start at
index 0 (such as `1 2` in the example) are never counted.

## Code

```python
n, k = [int(x) for x in input().split()]
a = [int(x) for x in input().split()]

seen = {0: 1}          # prefix sum 0 occurs once: the empty prefix before index 0
prefix = 0
count = 0
for x in a:
    prefix += x
    count += seen.get(prefix - k, 0)     # earlier prefixes p with prefix - p == k
    seen[prefix] = seen.get(prefix, 0) + 1

print(count)
```

Trace for the example (`k = 3`):

| x | prefix | prefix - k | seen before | count |
|---|---|---|---|---|
| 1 | 1 | -2 | {0:1} | 0 |
| 2 | 3 | 0 | {0:1, 1:1} | 1 |
| 1 | 4 | 1 | {0:1, 1:1, 3:1} | 2 |
| -1 | 3 | 0 | {0:1, 1:1, 3:1, 4:1} | 3 |
| 3 | 6 | 3 | {0:1, 1:1, 3:2, 4:1} | 5 |

At the last step `prefix - k = 3` was seen twice (after `1 2` and after `1 2 1 -1`), so two subarrays end
here: `1 -1 3` and `3`.

## Complexity

O(n) time on average (one dictionary lookup and one update per element) and O(n) extra memory for the
dictionary. The brute force over all pairs `(i, j)` is O(n^2): 2 * 10^10 steps for `n = 200000`.

## Another way

If all numbers were positive, a shrinking sliding window would count the subarrays in O(n) with O(1) memory.
With negative numbers the window can't decide when to shrink, which is why the prefix-count method is the
general tool. `collections.Counter` or `defaultdict(int)` can replace the `seen.get(..., 0)` calls.
