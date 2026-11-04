## Approach

Let `x = a ^ b`. Pairs cancel, so XOR of everything is `x`, and `x != 0`. Pick any set bit of `x`; the lowest is `low = x & -x`.
At that bit `a` and `b` differ. Partition all numbers by this bit. Both copies of a repeated value go to the same group,
so inside each group the pairs cancel in XOR, leaving one single value per group.

## Code

```python
n = int(input())
values = [int(v) for v in input().split()]

x = 0
for v in values:
    x ^= v
low = x & -x
a = 0
b = 0
for v in values:
    if v & low:
        a ^= v
    else:
        b ^= v
print(min(a, b), max(a, b))
```

## Complexity

Two passes: O(n) time and O(1) extra space (besides the list).

## Another way

A dict of counts: values with count 1 are the answer. O(n) time but O(n) extra space, and about 3 times slower for a
million numbers. Sorting and scanning in pairs is O(n log n).
