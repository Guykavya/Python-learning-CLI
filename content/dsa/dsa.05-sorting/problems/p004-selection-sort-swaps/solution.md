## Approach

The sorted prefix grows by one each round: find the minimum of the unsorted rest and swap it to the front. Count only real swaps.

## Code

```python
n = int(input())
a = [int(x) for x in input().split()]
swaps = 0
for i in range(n - 1):
    m = i
    for j in range(i + 1, n):
        if a[j] < a[m]:
            m = j
    if m != i:
        a[i], a[m] = a[m], a[i]
        swaps += 1
print(" ".join(map(str, a)))
print(swaps)
```

## Complexity

O(n^2) comparisons always (even if sorted), at most n - 1 swaps, O(1) extra memory.

## Another way

Selection sort is the method with the **fewest writes** (at most `n - 1` swaps). It is useful when moving data is expensive. It is not stable: swapping the minimum over a far element can jump an equal value past another equal value.
