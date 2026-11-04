## Approach

Only some elements can still become a window maximum: those with **no bigger-or-equal element after them** inside
the window. Those "candidates" form a decreasing sequence, and the deque stores exactly them, oldest at the front.

- New element `a[i]`: every candidate at the back with a value `<= a[i]` is dominated (smaller, and leaves earlier),
  so pop it. Then append `i`.
- The oldest candidate may be outside the window: drop it if its index is `<= i - k`.
- The front is the largest candidate in the window: the maximum.

## Code

```python
from collections import deque

n, k = [int(x) for x in input().split()]
a = [int(x) for x in input().split()]

dq = deque()
out = []
for i in range(n):
    while dq and a[dq[-1]] <= a[i]:
        dq.pop()
    dq.append(i)
    if dq[0] <= i - k:
        dq.popleft()
    if i >= k - 1:
        out.append(a[dq[0]])
print(*out)
```

Trace of the example, `k = 3` (deque shown as values):

| i | a[i] | deque after | output |
|---|---|---|---|
| 0 | 1 | 1 | |
| 1 | 3 | 3 | |
| 2 | -1 | 3 -1 | 3 |
| 3 | -3 | 3 -1 -3 | 3 |
| 4 | 5 | 5 | 5 |
| 5 | 3 | 5 3 | 5 |
| 6 | 6 | 6 | 6 |
| 7 | 7 | 7 | 7 |

## Complexity

O(n) time: every index is appended once and popped at most once, so the inner `while` runs at most `n` times in total.
The deque holds at most `k` indices.

## Another way

Cut the array into blocks of length `k`. Inside each block compute prefix maxima (left to right) and suffix maxima
(right to left). A window of length `k` covers the end of one block and the start of the next, so its maximum is
`max(suffix_max[i], prefix_max[i + k - 1])`. Also O(n), with no deque, but two extra arrays. A `heapq` with lazy
deletion is O(n log n) and works too.
