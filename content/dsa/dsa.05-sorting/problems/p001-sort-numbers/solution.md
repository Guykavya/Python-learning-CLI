## Approach

Convert to ints, call `sorted` once for the ascending line and `sorted(..., reverse=True)` for the descending line, then join with spaces.

## Code

```python
n = int(input())
a = [int(x) for x in input().split()]
print(" ".join(map(str, sorted(a))))
print(" ".join(map(str, sorted(a, reverse=True))))
```

## Complexity

O(n log n) time (Timsort), O(n) extra memory for the new lists.

## Another way

`a.sort()` sorts in place and avoids one copy. Then `a[::-1]` gives the descending order because the ascending list is exactly reversed (equal numbers are indistinguishable, so no stability worry for plain ints).
