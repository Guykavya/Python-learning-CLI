## Approach

Binary search the number `i` of elements taken from `A` among the `k` smallest. The test "`A[i] < B[k - i - 1]`" says that `i` is too small; it is monotone in `i`. When the split is found, the k-th smallest is the larger of the two elements just before the split.

## Code

```python
n, m, k = map(int, input().split())


def A(i):
    print("? A", i, flush=True)
    return int(input())


def B(j):
    print("? B", j, flush=True)
    return int(input())


lo, hi = max(0, k - m), min(k, n)
while lo < hi:
    i = (lo + hi) // 2
    j = k - i
    if A(i) < B(j - 1):
        lo = i + 1
    else:
        hi = i
i = lo
j = k - i
best = []
if i > 0:
    best.append(A(i - 1))
if j > 0:
    best.append(B(j - 1))
print("!", max(best), flush=True)
```

## Complexity

O(log min(n, k)) questions (two per step), O(1) memory.

## Another way

Binary search on the **value** `x`: count how many elements of `A` and `B` are `<= x` (two lower-bound searches) and find the smallest `x` with count `>= k`. It needs about `log(range) * log(n)` questions, too many for the limit here, but it is easier to write when the arrays are in memory.
