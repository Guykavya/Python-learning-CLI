**A. Pass.** A set of 20 items has `2^20 = 1048576` subsets, about 10^6. Even with ~20 steps to add up each
subset, that is 2 * 10^7: around a second in plain Python, comfortable with a smarter way of summing. `n <= 20` is
the classic signal that O(2^n) is intended.

**B. Pass.** About `2000 * 2000 / 2 = 2 * 10^6` pairs. Fine. `n` up to a few thousand allows O(n^2).

**C. Fail.** About `200000^2 / 2 = 2 * 10^10` pairs: about half an hour in Python. Need O(n log n) or better.
Approach: sort the numbers (O(n log n)); the two closest values must then be neighbours, so one pass over adjacent
pairs finds them.

**D. Fail.** Up to 10^12 divisions: about a day. Need about O(sqrt(n)): if `n` has a divisor other than 1 and
itself, it has one at most `sqrt(n)`, so try divisors only up to `sqrt(10^12) = 10^6`. That is 10^6 steps: fine.

**E. Fail.** `n * q = 10^10` steps. Need about O((n + q) log n). Approach: sort the numbers once, then answer each
question with binary search (about 17 steps each). Or, if the values are small, precompute counts.

**F. Pass, but only just.** `10! = 3628800` orders, each needing ~10 additions: about 3.6 * 10^7 steps,
a few seconds in Python, faster with care. `n <= 10` (or 11) is the signal that O(n!) is intended; at `n = 13` it
would be 6 * 10^9, hopeless.

**G. Fail.** 10^18 steps would take thousands of years. Need O(1): the formula `n * (n + 1) // 2`.

**First thing.** I read the constraints before thinking about a solution, and compute what the largest input
allows: about 10^7 simple operations per second in Python. That tells me the complexity I need (for example
`n <= 2 * 10^5` means O(n log n) or O(n)), which rules out wrong ideas before I write them, and often hints at
the intended technique (`n <= 20` suggests subsets, `n <= 10^18` suggests a formula or something logarithmic).

Key ideas to check: A 2^20 ~ 10^6 passes; B 2 * 10^6 passes; C 2 * 10^10 fails, sort then compare neighbours,
O(n log n); D 10^12 fails, divisors up to sqrt n = 10^6; E 10^10 fails, sort + binary search; F 10! ~ 3.6 * 10^6
passes; G needs O(1) formula; constraints first, about 10^7 Python operations per second.
