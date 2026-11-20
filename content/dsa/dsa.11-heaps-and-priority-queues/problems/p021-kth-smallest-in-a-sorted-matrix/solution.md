## Approach

Every row is a sorted list, so the matrix is `n` sorted lists to merge. The `k`-th smallest is found by merging only `k` steps. The heap holds one cell per row: the front cell of that row that has not been taken yet. After popping a cell, the only new candidate is its right neighbour (the cells below are already in the heap through their own rows, or are bigger than a cell above them). Only the first `min(n, k)` rows can matter at the start: a cell in row number `k + 1` (counting from 1) has `k` cells above it in its column, all smaller or equal, so at least `k` numbers are `<=` it. So the `k`-th smallest value is already reached among the first `k` rows, and the other rows can be left out. (With `k = 1000` and 1,000 rows this saves nothing; with `k = 5` it saves 995 heap entries.)

## Code

```python
import heapq

def kth_smallest(matrix, k):
    n, m = len(matrix), len(matrix[0])
    heap = [(matrix[r][0], r, 0) for r in range(min(n, k))]
    heapq.heapify(heap)
    for _ in range(k - 1):
        value, r, c = heapq.heappop(heap)
        if c + 1 < m:
            heapq.heappush(heap, (matrix[r][c + 1], r, c + 1))
    return heap[0][0]
```

## Complexity

`O(min(n, k) + k log min(n, k))` time, `O(min(n, k))` memory, and only about `min(n, k) + k` cells are read.

## Another way

**Binary search on the value.** The answer lies between `matrix[0][0]` and `matrix[-1][-1]`. For a candidate `x`, count the cells `<= x` in `O(n + m)` by a staircase walk from the bottom-left corner. The smallest `x` with `count(x) >= k` is the answer (it is always a number of the matrix). Time `O((n + m) log(range))`, memory `O(1)`; it reads about `2 (n + m)` cells per step, so for large `k` it beats the heap, and for tiny `k` the heap wins.

```python
def kth_smallest(matrix, k):
    n, m = len(matrix), len(matrix[0])
    lo, hi = matrix[0][0], matrix[-1][-1]
    while lo < hi:
        mid = (lo + hi) // 2
        count, r, c = 0, n - 1, 0
        while r >= 0 and c < m:
            if matrix[r][c] <= mid:
                count += r + 1
                c += 1
            else:
                r -= 1
        if count >= k:
            hi = mid
        else:
            lo = mid + 1
    return lo
```

(This version assumes integers.) Flattening and sorting is the third way: simple, `O(nm log nm)` time and `O(nm)` memory; the tests reject it by counting reads.
