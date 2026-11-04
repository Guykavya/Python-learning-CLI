## Approach

Keep the invariant "if the target is present, it lies in `a[lo..hi]`". Compare with the middle element, discard the half that cannot contain the target (and `mid` itself), and stop when the range is empty.

## Code

```python
n = int(input())
a = [int(x) for x in input().split()]
q = int(input())
targets = [int(x) for x in input().split()]
out = []
for x in targets:
    lo, hi = 0, n - 1
    ans = -1
    while lo <= hi:
        mid = (lo + hi) // 2
        if a[mid] == x:
            ans = mid
            break
        elif a[mid] < x:
            lo = mid + 1
        else:
            hi = mid - 1
    out.append(ans)
print("\n".join(map(str, out)))
```

## Complexity

O(q log n) time, O(1) extra memory besides the input.

## Another way

Use the half-open lower bound (chapter section 5): find the first index with `a[i] >= x`, then check `i < n and a[i] == x`. The result is the same, and the same function also answers "where would x be inserted".
