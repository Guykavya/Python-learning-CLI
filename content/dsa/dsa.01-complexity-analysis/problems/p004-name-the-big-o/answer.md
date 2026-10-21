**A: O(n).** The loop body runs once per element of `a`, so `n` times. Each pass does one addition, which is
constant time.

**B: O(n^2).** The comparison runs `(n - 1) + (n - 2) + ... + 1 + 0 = n(n - 1)/2` times. That is about `n^2 / 2`,
and we drop the constant `1/2`.

**C: O(log n).** Each pass halves `n`. Starting from `n`, you can halve only about `log2 n` times before
reaching 1. For `n = 10^6` that is about 20 passes.

**D: O(n log n).** The outer loop runs `n` times. For each of them, the inner loop doubles `k` from 1 until it
reaches `n`, which takes about `log2 n` steps. The inner loop does not depend on `i`, so the total is
`n * log2 n`.

**E: O(n).** The inner loop runs `n` times for each of 100 outer passes: `100n` prints. 100 is a constant
(it does not grow with the input), so this is O(n). It is a slow O(n), though: in practice 100 times the work of A.

**F: O(n + m).** The loops are one after the other, so their costs add: `n + m`. You cannot simplify to O(n)
because `m` could be much bigger than `n`. If you know `m <= n`, it is O(n).

**G: O(n * m).** The loop runs `n` times, and `x in b` is **itself a loop**: Python scans the list `b` from the
start until it finds `x` or reaches the end. That scan is O(m) in the worst case (when `x` is missing). So the
total is `n * m`, and O(n^2) if both lists have size `n`. Converting `b` to a set first (`bs = set(b)`, cost
O(m)) makes each `x in bs` O(1) on average, and the total becomes O(n + m).

Key ideas to check: count how often the innermost line runs; nested loops multiply and sequential loops add;
halving gives log n; constants like 100 and 1/2 are dropped; two different sizes stay as two letters; `in` on a list
is a hidden O(m) loop.
