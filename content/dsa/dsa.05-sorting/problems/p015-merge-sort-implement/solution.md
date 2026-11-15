## Approach

Divide, conquer, combine. The recursion is `log2(n)` levels deep and each level merges `n` elements in total.

## Code

```python
n = int(input())
a = [int(x) for x in input().split()]


def merge(left, right):
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
    return out


def merge_sort(a):
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    return merge(merge_sort(a[:mid]), merge_sort(a[mid:]))


print(" ".join(map(str, merge_sort(a))))
```

## Complexity

O(n log n) time in every case; O(n) extra memory for the merges; recursion depth O(log n); stable when ties take the left value first.

## Another way

Bottom-up merge sort: start with runs of length 1 and merge neighbours with widths 1, 2, 4, ... No recursion, and a good tool when recursion depth worries you. Or sort `lo..hi` ranges in place with one auxiliary buffer to avoid slicing.
