## Hint 1

Look at one row: its smallest number is the first. Look at the whole matrix: where must the smallest number be? And the second smallest: it is next to a number that you have already taken. Which neighbours? Compare with merging `n` sorted lists (the rows) and stopping after `k` numbers.

## Hint 2

Put the first cell of every row (only the first `min(n, k)` rows matter) in a min-heap as `(value, row, column)`. Pop the smallest `k - 1` times; after each pop, push the cell to the **right** of the one you popped (same row, next column), if there is one. After `k - 1` pops, the top of the heap is the `k`-th smallest.

## Hint 3

```
heap = [(matrix[r][0], r, 0) for r in range(min(n, k))]
heapify(heap)
repeat k - 1 times:
    value, r, c = pop(heap)
    if c + 1 < m: push(heap, (matrix[r][c + 1], r, c + 1))
return heap[0][0]
```

Another way (no heap): binary search on the **value**. For a value `x`, count the cells `<= x` by walking from the bottom-left corner: if the cell is `<= x`, the whole column above it counts (add `row + 1`) and you move right; otherwise move up. Find the smallest `x` whose count is at least `k`.
