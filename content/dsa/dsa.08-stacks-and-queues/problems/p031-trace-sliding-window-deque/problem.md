# Trace: the sliding window deque

This is the chapter's sliding window maximum (section 11), printing the deque of **indices** after every step. It runs on two inputs. Predict **exactly** what it prints. Do not run it.

```python
from collections import deque


def trace(nums, k):
    dq = deque()                       # indices, values decreasing from front to back
    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            print(i, list(dq), nums[dq[0]])
        else:
            print(i, list(dq), "-")


trace([1, 3, -1, -3, 5, 3, 6, 7], 3)
print("next")
trace([5, 4, 3, 2, 6, 1], 3)
```

Write your answer in `answer.txt`, one printed line per line: the index `i`, the deque as a list of **indices**, and the window maximum (or `-` while the first window is not complete), for example `2 [1, 2] 3`. Between the two runs there is a line `next`.

## How to work

At every step, in this order:

1. **back**: pop indices from the right while their value is `<=` the new value;
2. append `i`;
3. **front**: if the front index is `<= i - k`, it has left the window: pop it from the left;
4. print.

Write both the indices and their values on paper, but print only the indices.

## After you answer

1. In the first run, does the front check (step 3) ever remove anything? Why not?
2. In the second run, at which `i` does the front check fire, and which value would be reported wrongly without it?
3. Why is the window maximum always `nums[dq[0]]`?
