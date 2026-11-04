## Approach

Build a heap in `O(n)`, then take the maximum `n - 1` times. Each extraction costs `O(log n)`, and the list is sorted ascending from the back.

## Code

```python
n = int(input())
a = [int(x) for x in input().split()]


def sift_down(a, i, size):
    while True:
        left = 2 * i + 1
        right = 2 * i + 2
        big = i
        if left < size and a[left] > a[big]:
            big = left
        if right < size and a[right] > a[big]:
            big = right
        if big == i:
            return
        a[i], a[big] = a[big], a[i]
        i = big


for i in range(n // 2 - 1, -1, -1):
    sift_down(a, i, n)
for end in range(n - 1, 0, -1):
    a[0], a[end] = a[end], a[0]
    sift_down(a, 0, end)
print(" ".join(map(str, a)))
```

## Complexity

O(n log n) time in every case, O(1) extra memory (in place), not stable.

## Another way

Use `heapq` with a min-heap: push all values (or `heapify`) and pop `n` times. It is `O(n log n)` too but allocates a new list. Heap sort is the sort with the best **worst-case plus constant memory** guarantee; it is slower than quick sort in practice because of cache misses.
