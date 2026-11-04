## Approach

Binary search on the answer with the half-open template. The reply to a question is exactly the predicate value; the first True is `B`.

## Code

```python
n = int(input())
lo, hi = 1, n
while lo < hi:
    mid = (lo + hi) // 2
    print("?", mid, flush=True)
    if int(input()) == 1:
        hi = mid
    else:
        lo = mid + 1
print("!", lo, flush=True)
```

## Complexity

O(log n) questions, O(1) memory.

## Another way

Closed template with `ans = n`: `if bad(mid): ans = mid; hi = mid - 1 else lo = mid + 1`. It asks the same number of questions.
