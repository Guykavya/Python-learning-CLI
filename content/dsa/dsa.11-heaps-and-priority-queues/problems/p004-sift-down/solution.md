## Approach

The item at `i` is the only one that can break the rule, and only against its children. The two subtrees below are heaps, so the **smaller** of the two children is the right new parent: it is not larger than the other child, and it is not larger than anything below. Swap with it and repeat one level lower. The loop ends when no child is smaller or when `i` has become a leaf (both child indexes are `>= n`). Each step goes one level down: at most `log2(n)` steps.

## Code

```python
def sift_down(a, i, n):
    while True:
        smallest = i
        l, r = 2 * i + 1, 2 * i + 2
        if l < n and a[l] < a[smallest]:
            smallest = l
        if r < n and a[r] < a[smallest]:
            smallest = r
        if smallest == i:
            break
        a[i], a[smallest] = a[smallest], a[i]
        i = smallest
```

## Complexity

`O(log n)` time, `O(1)` extra memory. Two comparisons per level.

## Another way

A recursive version (`sift_down(a, smallest, n)` at the end instead of the loop) does the same with `O(log n)` stack. `heapq` does something different on a pop: it moves the hole **all the way down** to a leaf along the smaller children, puts the item there, and then bubbles it up. That uses fewer comparisons on average, because the item usually belongs near the bottom anyway; the final heap can differ from the textbook version, but it is just as valid.
