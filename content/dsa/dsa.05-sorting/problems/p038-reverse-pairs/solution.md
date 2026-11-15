## Approach

Merge sort with a counting phase before each merge: both halves are sorted, so for increasing `j` the qualifying left values form a shrinking suffix, found with one forward-moving pointer.

## Code

```python
n = int(input())
a = [int(x) for x in input().split()]


def sort_count(a):
    if len(a) <= 1:
        return a, 0
    mid = len(a) // 2
    left, x = sort_count(a[:mid])
    right, y = sort_count(a[mid:])
    cross = 0
    i = 0
    for r in right:
        while i < len(left) and left[i] <= 2 * r:
            i += 1
        cross += len(left) - i
    out = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out, x + y + cross


print(sort_count(a)[1])
```

## Complexity

O(n log n) time, O(n) memory.

## Another way

A Fenwick tree over the compressed values of all `a[i]` and `2 * a[i]`: scan left to right, count earlier values `> 2 * a[j]`, then insert `a[j]`. Same complexity, and it generalises to 'count of smaller numbers after self' (LeetCode 315).
