## Approach

The deque holds the indices that could still become a window maximum: values strictly decreasing from front to back. A new value removes everything at the back that it beats; the front is removed when it slides out of the window. The front is then the maximum of the current window.

## Code

```python
from collections import deque


def window_max(nums, k):
    dq = deque()                       # indices, values decreasing from front to back
    out = []
    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out
```

## Complexity

`O(n)` time: every index is appended once and removed at most once (from the back **or** the front, never both). `O(k)` memory for the deque, plus the output.

## Another way

Split `nums` into blocks of size `k`. Compute prefix maximums inside each block from the left, and suffix maximums from the right. A window covers the end of one block and the start of the next, so its maximum is `max(suffix[i], prefix[i + k - 1])`. Also `O(n)`, with no deque, but two extra arrays.
