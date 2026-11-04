**1. Meaning.** Let `add[i]` be the total amount added to position `i` by all updates. Then `d[i] = add[i] - add[i - 1]`
(with `add[-1] = 0`): `d` is the array of **differences** of `add`. Summing differences from the start gives back the
values: `d[0] + ... + d[i] = add[i]`, because the sum telescopes.

**2. One update.** `n = 6`, `l = 1`, `r = 3`, `v = 5`: `d = [0, 5, 0, 0, -5, 0, 0]` (7 slots). Running totals for
`i = 0..5`: `0, 5, 5, 5, 0, 0`. The `+5` at `l` makes every total from `l` onwards 5 higher; the `-5` at `r + 1` cancels it
from `r + 1` onwards. If the `-5` were at `r`, position `r` itself would lose the update: the range is inclusive.

**3. Many updates.** Each update adds its own small difference array to `d`. The prefix sum is linear: the prefix sum
of a sum of arrays is the sum of their prefix sums. So one pass at the end gives every update's effect added
together, in any order of the updates.

**4. Extra slot.** For `r = n - 1` the code writes `d[n] -= v`. With only `n` slots that is an `IndexError`. The slot is
never read by the final loop (it only runs to `n - 1`), so it is a harmless "parking place" that saves an `if`.

**5. Cost.** Plain loop: O(length of the range) per update, O(q * n) in the worst case: 2 * 10^5 updates of the whole
array of 2 * 10^5 is 4 * 10^10 additions. Difference array: O(1) per update plus O(n) once: O(n + q). The plain loop
is fine when there are few updates, the ranges are short, or you need the array **between** updates (the difference
array only gives values after the prefix pass).

**6. Inverse.** Prefix sum: `P[i] = a[0] + ... + a[i]`. Difference: `d[i] = a[i] - a[i - 1]`. Taking the prefix sum of the
differences gives back `a`, and taking the differences of the prefix sums gives back `a` too, like integration and
differentiation. A range query on `a` is two points on `P`; a range update on `a` is two points on `d`.

**Common traps.** Putting `-v` at `r`. Forgetting to add the running total to the **original** array (the totals are the
amounts added, not the new values). Reading the array between updates without doing the prefix pass first.
