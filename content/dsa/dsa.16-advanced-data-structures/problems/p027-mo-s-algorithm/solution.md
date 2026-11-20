## Approach

Chapter section 16. Keep a window and its answer; move to the next question one element at a time, adding or removing in `O(1)`. Process the questions in Mo's order, sorted by `(l // B, r)` (with the right edge alternating direction in odd blocks, a common refinement), so that the total movement is about `(n + q) * sqrt(n)`.

```python
import math


def distinct_counts(a, queries):
    n = len(a)
    B = max(1, math.isqrt(n))
    order = sorted(range(len(queries)),
                   key=lambda i: (queries[i][0] // B,
                                  queries[i][1] if (queries[i][0] // B) % 2 == 0 else -queries[i][1]))
    count = {}
    distinct = 0
    cur_l = cur_r = 0                        # the window a[cur_l:cur_r], empty at first
    answers = [0] * len(queries)
    for qi in order:
        l, r = queries[qi]
        while cur_l > l:                     # grow first ...
            cur_l -= 1
            x = a[cur_l]
            count[x] = count.get(x, 0) + 1
            distinct += count[x] == 1
        while cur_r < r:
            x = a[cur_r]
            count[x] = count.get(x, 0) + 1
            distinct += count[x] == 1
            cur_r += 1
        while cur_l < l:                     # ... then shrink
            x = a[cur_l]
            count[x] -= 1
            distinct -= count[x] == 0
            cur_l += 1
        while cur_r > r:
            cur_r -= 1
            x = a[cur_r]
            count[x] -= 1
            distinct -= count[x] == 0
        answers[qi] = distinct
    return answers
```

Grow before shrinking: if the right edge shrank first while `cur_l` was still larger than the new `r`, the window would become "negative" and counts would drop below zero.

## Complexity

Sorting `O(q log q)`; window movement `O((n + q) sqrt n)`; memory `O(n + q)`. No updates allowed.

## Another way

Offline Fenwick sweep (chapter section 17): sort the questions by `r`; sweep `i` and keep a 1 only at the **last** occurrence of every value so far; the answer for `[l, r)` is the number of 1s in `[l, r)` when the sweep is at `r - 1`. `O((n + q) log n)`, often faster than Mo's in Python.
