## Hint 1

Suppose you decide that the `k` smallest elements contain exactly `i` elements of `A` and `k - i` of `B`. What two inequalities between neighbours must hold for this to be a correct split?

## Hint 2

Check the split `i`: if `A[i] < B[k - i - 1]`, then `A[i]` is smaller than something that was counted in, so `i` is too small: `lo = i + 1`. Otherwise `hi = i`. The valid range for `i` is `[max(0, k - m), min(k, n)]`, so that both `A[i]` and `B[k - i - 1]` exist when you read them (`i < hi <= n` and `k - i >= 1`).

## Hint 3

```
lo, hi = max(0, k - m), min(k, n)
while lo < hi:
    i = (lo + hi) // 2
    j = k - i
    if A(i) < B(j - 1): lo = i + 1
    else: hi = i
i = lo; j = k - i
candidates = []
if i > 0: candidates.append(A(i - 1))
if j > 0: candidates.append(B(j - 1))
print("!", max(candidates))
```
