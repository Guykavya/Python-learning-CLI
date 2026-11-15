## Approach

Build the two ambiguous arrays, show the three numbers `a[lo]`, `a[mid]`, `a[hi]` are identical, and argue that dropping one equal element is safe because its twin stays. Then give the all-equal-but-one input for the worst case.

## Model answer

See `answer.md`. Compare it with yours point by point.

## What to check

- Two arrays with identical `a[lo]`, `a[mid]`, `a[hi]` and the minimum on different sides, such as `[3, 3, 3, 1, 3]` and `[3, 1, 3, 3, 3]`.
- `hi -= 1` is safe: the value `a[hi]` also exists at `mid`.
- A counterexample for `hi = mid`: `[3, 3, 3, 1, 3]` with `mid = 2`.
- Worst case O(n), for example `[1, 1, 1, 1, 0, 1, 1]`, and a proof sketch that no algorithm can be faster.
- Typical case: few duplicates, so about O(log n).
