**1. The property.** With positive numbers the window sum is *monotonic*: adding an element on the right always
makes the sum **bigger**, and removing an element on the left always makes it **smaller**. So, once a window reaches
`s`, a longer window ending at the same `r` can only be bigger (no need to keep it), and when the sum is below `s`,
shrinking can never help. Those two facts justify "shrink while `>= s`, otherwise grow".

**2. Counterexample.** `a = 5 -10 3 4`, `s = 7`.

| r | a[r] | total |
|---|---|---|
| 0 | 5 | 5 |
| 1 | -10 | -5 |
| 2 | 3 | -2 |
| 3 | 4 | 2 |

`total` never reaches 7, the `while` never runs, and the code prints `0`. The right answer is `2`: the subarray
`3 4` has sum 7.

**3. Why it fails.** The window keeps `5 -10` at its left end. Dropping that prefix would **raise** the sum from 2 to
7, but the code only drops elements when the sum is already big enough; it assumes that dropping always lowers the
sum. With negative numbers, a bad prefix (one with a negative sum) can hide a good subarray, and the window never
looks back to remove it.

**4. Exact sums.** For `1 -1 1` and `k = 1` the right count is 3: `1` (first), `1 -1 1`, and `1` (last). A window
that shrinks while the sum is `> k` and counts when it equals `k` sees sums 1, 0, 1 with the left end always at 0. It
counts the first `1` and the whole array, but never the last `1` alone, because that would need dropping `1 -1`,
whose sum is 0 and does not make the total "too big". So it counts 2.

**5. What to use instead.**
(a) Prefix sums plus a dictionary of how often each prefix sum appeared: count `seen[P - k]` at each step. O(n).
(b) Prefix sums plus a dictionary of the **first** index of each prefix sum; length `j - first[P - k]`. O(n).
(c) Prefix sums plus a **monotonic deque** of candidate start positions with increasing prefix sums. O(n). (A
    sorted structure with binary search also works in O(n log n).)
(d) Kadane's algorithm: `cur = max(x, cur + x)`. O(n). It handles negatives by design.

**Common traps.** Thinking the window "just needs a `while` instead of an `if`": the problem is the missing
monotonicity, not the loop. Forgetting that zeros are harmless (sums stay monotonic, only not strictly) while a single
negative number can break it.
