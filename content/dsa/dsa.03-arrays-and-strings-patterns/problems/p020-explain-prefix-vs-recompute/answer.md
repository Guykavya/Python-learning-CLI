**1. Program A.** Each question adds `r - l + 1` numbers. The worst questions cover the whole array, so A can do
`q * n = 200000 * 200000 = 4 * 10^10` additions. At roughly 10^7 simple Python steps per second, that is over an hour.

**2. Program B.** Building `p` takes `n` additions. Each question is then two list reads and one subtraction, the same
work whether the range has 1 element or 200000. Total about `n + q` steps: `400000` for the example, a fraction of a
second. We paid once up front so that each question is O(1).

**3. Why it works.** `p[i]` is the sum of the first `i` elements. `p[r] = a[1] + ... + a[r]` and
`p[l-1] = a[1] + ... + a[l-1]`, so the subtraction cancels everything before `l` and leaves `a[l] + ... + a[r]`.
`p[0] = 0` is the sum of no elements; it makes `l = 1` work without a special case (`p[r] - p[0] = p[r]`).
Example: `a = 3 -1 4 1 5`, `p = 0 3 2 6 7 12`, sum of `2..5` is `12 - 3 = 9`.

**4. Memory.** B keeps `n + 1` extra integers. That is usually cheap, but it is extra memory. A is fine (and simpler)
when there are only a few questions, or when the ranges are always short: then `q * (range length)` is small.

**5. Updates.** Changing `a[i]` changes every `p[j]` with `j >= i`: up to `n` cells. If you rebuild after each change,
updates cost O(n) each and you are back to `n * q`. Prefix sums are for arrays that do not change between questions.
(Structures such as a Fenwick tree or segment tree handle both updates and sums in O(log n); they come later.)
