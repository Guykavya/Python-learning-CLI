## Approach

Prefix sums turn "sum of a subarray" into "difference of two prefixes". For every end `i`, the longest good subarray
starts right after the **earliest** index `j` with `P[j] = P[i] - k`. A dictionary from prefix value to its first index
gives that `j` in O(1). Storing `P[0] = 0` at index 0 makes subarrays that start at the first element work like all
the others.

Why not a sliding window? A window needs "adding makes the sum bigger, removing makes it smaller". With negative
values that is false: in `5 -5 3` with `k = 3`, the window drops the 5 for being too big, but the -5 would have
brought the sum back down.

## Code

```python
n, k = [int(x) for x in input().split()]
a = [int(x) for x in input().split()]

first = {0: 0}
best = 0
pre = 0
for i in range(1, n + 1):
    pre += a[i - 1]
    j = first.get(pre - k)
    if j is not None and i - j > best:
        best = i - j
    if pre not in first:
        first[pre] = i
print(best)
```

## Complexity

O(n) time (one pass, O(1) dictionary work per step) and O(n) memory for the dictionary.

## Another way

Store the **last** index of each prefix value instead, and loop over the **start** `j`: the longest subarray starting
right after `j` ends at the last `i` with `P[i] = P[j] + k`. Same idea, mirrored. The counting version of this pattern
(how many subarrays have sum `k`) stores **how many times** each prefix value appeared instead of where.
