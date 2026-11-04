## Approach

For each template write down: initial range, loop condition, updates, invariant, final state. Then connect the bugs to broken invariants: a wrong initial `hi` removes a valid answer; a `lo = mid` without rounding up stops the range from shrinking.

## Model answer

See `answer.md`. Compare it with yours point by point.

## What to check

- Closed: `lo = 0, hi = n - 1`, `while lo <= hi`, `lo = mid + 1` / `hi = mid - 1`, invariant "target in [lo, hi] if present", ends with `lo = hi + 1`.
- Half-open: `lo = 0, hi = n`, `while lo < hi`, `lo = mid + 1` / `hi = mid`, `lo == hi` at the end and it is the insertion point (first True).
- Shrink: closed range, `hi = n - 1`, `lo < hi`, an answer is guaranteed to exist (otherwise check at the end).
- Mixing example, e.g. `[1, 2, 3]`, x = 9 gives 2 instead of 3.
- Round-up mid with `lo = 3, hi = 4` shows the infinite loop.
- A recommendation with a reason: one template means one invariant to remember and fewer bugs.
