## Approach

In a rotated sorted array one of the two halves around `mid` is always sorted. Test the target against the bounds of the sorted half; if it fits there go there, otherwise go to the other half.

## Code

```python
n = int(input())
a = [int(x) for x in input().split()]
q = int(input())
queries = [int(x) for x in input().split()]
out = []
for x in queries:
    lo, hi = 0, n - 1
    ans = -1
    while lo <= hi:
        mid = (lo + hi) // 2
        if a[mid] == x:
            ans = mid
            break
        if a[lo] <= a[mid]:
            if a[lo] <= x < a[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:
            if a[mid] < x <= a[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    out.append(ans)
print("\n".join(map(str, out)))
```

## Complexity

O(q log n) time, O(1) extra space.

## Another way

Find the index `k` of the minimum with the previous problem. Then the array is two sorted pieces: binary search on `a[k:]` or `a[:k]` depending on `x` compared with `a[0]`. Or treat position `i` as `a[(i + k) % n]` and run a plain binary search on the virtual sorted array.
