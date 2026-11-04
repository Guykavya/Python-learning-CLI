## Approach

Repeat passes over adjacent pairs; a pass without swaps proves the list is sorted. Count passes and swaps along the way.

## Code

```python
n = int(input())
a = [int(x) for x in input().split()]
passes = swaps = 0
while True:
    passes += 1
    swapped = False
    for i in range(n - 1):
        if a[i] > a[i + 1]:
            a[i], a[i + 1] = a[i + 1], a[i]
            swaps += 1
            swapped = True
    if not swapped:
        break
print(passes)
print(swaps)
print(" ".join(map(str, a)))
```

## Complexity

Worst case O(n^2) (reversed: n passes, n(n-1)/2 swaps); best case O(n) for sorted input; O(1) extra memory; stable.

## Another way

Passes can be predicted without simulating: it is `1 + max over elements of (number of larger elements before it)`, because each pass moves an element at most one place left. You can also shrink the inner loop by one each pass since the largest values settle at the end.
