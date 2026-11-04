## Approach

Maintain a sorted prefix. Take the next element, shift larger prefix elements right, and drop the element into the gap. Each shift removes exactly one inversion.

## Code

```python
n = int(input())
a = [int(x) for x in input().split()]
shifts = 0
for i in range(1, n):
    key = a[i]
    j = i - 1
    while j >= 0 and a[j] > key:
        a[j + 1] = a[j]
        shifts += 1
        j -= 1
    a[j + 1] = key
print(" ".join(map(str, a)))
print(shifts)
```

## Complexity

Worst case O(n^2) (reverse order, n(n-1)/2 shifts); best case O(n) (sorted input); O(1) extra memory; stable.

## Another way

Count the inversions with merge sort in O(n log n) (problem p016). Or find the insertion spot with binary search (fewer comparisons) while still shifting the same number of elements.
