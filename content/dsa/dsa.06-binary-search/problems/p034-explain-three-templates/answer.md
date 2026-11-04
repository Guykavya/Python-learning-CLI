**1. Closed `[lo, hi]`.** Start `lo = 0, hi = n - 1`; loop `while lo <= hi`; if `a[mid] < x` then `lo = mid + 1`, if `a[mid] > x` then `hi = mid - 1`, and `==` returns.
Invariant: if `x` is in the array, its index is in `[lo, hi]`. Both updates throw `mid` away because it was just tested. The loop ends when the range is empty, `lo = hi + 1`.

**2. Half-open `[lo, hi)`.** Start `lo = 0, hi = n`; loop `while lo < hi`; `a[mid] < x` gives `lo = mid + 1`, otherwise `hi = mid`.
Invariant: all elements before `lo` are `< x`, all elements from `hi` on are `>= x`. At the end `lo == hi` is the first index with `a[i] >= x`, the insertion point (it can be `n`). Found or not found is a separate check: `lo < n and a[lo] == x`.

**3. Shrink.** Range `[lo, hi]` closed with `hi = n - 1`, `while lo < hi`, `hi = mid` or `lo = mid + 1`. At the end one index is left. It is right when an answer is **guaranteed** to exist, like "the first bad version" or "the minimum of a rotated array", since there is no "not found" outcome.

**4. Mixing.** Starting `hi = n - 1` and using `while lo < hi` with `hi = mid` removes the value `n` from the possible answers. For `[1, 2, 3]` and `x = 9` the loop ends with `lo = 2` (the last element), but the insertion point is 3.

**5. Round-up mid.** When the update is `lo = mid` (to keep a True), `mid` must lean right: with `lo = 3, hi = 4`, `(3 + 4) // 2 = 3`, so `lo = 3` again and the loop never ends. `(3 + 4 + 1) // 2 = 4` makes progress.

**6. Recommendation.** I would keep the half-open template: it handles found, not found, first and last occurrence, and insertion point with one picture. Mixing templates is where off-by-one bugs come from, because each template has its own initial value, condition and updates that only work together.
