## Approach

Compare against a correct merge sort: ties take the left element (`<=`), both leftovers are appended, and the two halves are `a[:mid]` and `a[mid:]`.

## Code

```python
n = int(input())
rows = []
for _ in range(n):
    key, label = input().split()
    rows.append((int(key), label))


def merge_sort(a):
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    left = merge_sort(a[:mid])
    right = merge_sort(a[mid:])
    out = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i][0] <= right[j][0]:
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out


for key, label in merge_sort(rows):
    print(key, label)
```

## Complexity

O(n log n) time, O(n) memory, stable. Because the tests include 100000 records with only five distinct keys, an unstable or lossy version fails quickly.

## Another way

Write the same sort bottom-up (merge runs of width 1, 2, 4, ...): the same three details (ties, leftovers, boundaries) decide whether it is correct. Or let Python do it with `sorted(rows, key=lambda r: r[0])`, which is stable, in real programs.
