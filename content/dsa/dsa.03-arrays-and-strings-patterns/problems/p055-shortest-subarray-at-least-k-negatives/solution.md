## Approach

Shortest subarray with sum at least `k` = for each end `i`, the **latest** start `j < i` with `P[j] <= P[i] - k`.
A deque of candidate starts handles both ends:

- **Front pops** (record answers). If `P[i] - P[front] >= k`, the start `front` works with end `i`. Every later end
  would make that subarray longer, so its best answer is now: record `i - front` and remove it. Keep popping: the next
  front may work too, and is even shorter.
- **Back pops** (remove dominated starts). If `P[back] >= P[i]`, then for any future end `e`,
  `P[e] - P[i] >= P[e] - P[back]` and `e - i < e - back`. Start `i` is at least as good in sum **and** strictly
  shorter, so `back` is useless.

After the back pops the deque's prefix values increase from front to back, which is exactly why checking only the
front is enough: if the front does not reach `k`, nothing behind it (with a bigger prefix) does.

## Code

```python
from collections import deque

n, k = [int(x) for x in input().split()]
a = [int(x) for x in input().split()]

P = [0] * (n + 1)
for i in range(n):
    P[i + 1] = P[i] + a[i]

best = n + 1
dq = deque()
for i in range(n + 1):
    while dq and P[i] - P[dq[0]] >= k:
        best = min(best, i - dq.popleft())
    while dq and P[dq[-1]] >= P[i]:
        dq.pop()
    dq.append(i)
print(best if best <= n else -1)
```

Trace `2 -1 2`, `k = 3`, `P = 0 2 1 3`:

| i | P[i] | front pops | back pops | deque after (indices) | best |
|---|---|---|---|---|---|
| 0 | 0 | | | 0 | - |
| 1 | 2 | 2 - 0 < 3 | | 0 1 | - |
| 2 | 1 | 1 - 0 < 3 | P[1] = 2 >= 1: pop 1 | 0 2 | - |
| 3 | 3 | 3 - 0 >= 3: length 3, pop 0; 3 - 1 < 3 | | 2 3 | 3 |

## Complexity

O(n) time: each of the `n + 1` indices is appended once and popped at most once. O(n) memory for the prefix list and
the deque.

## Another way

Keep the same increasing stack of starts (back pops only) and, for each `i`, **binary search** it for the last start
with `P[j] <= P[i] - k`. That is O(n log n) and does not need the front pops. It is a good way to check the deque
version, and it shows the two halves of the trick separately: the back pops make the candidates sorted; the front
pops just save the binary search.
