The model answer is shown when you check. The ideas that must appear:

1. A: `2^20` is about 10^6: passes. Small `n` like 20 signals exponential search.
2. B: about 2 * 10^6 pairs: passes.
3. C: about 2 * 10^10 pairs: fails. Sort, then compare neighbours: O(n log n).
4. D: 10^12 divisions fails; check divisors only up to `sqrt(n)` = 10^6.
5. E: 10^10 fails; sort once and binary search each question: O((n + q) log n).
6. F: `10!` is about 3.6 * 10^6: passes (borderline in Python with the extra work per order).
7. G: needs a formula, O(1).
8. Read constraints first; they tell you the needed complexity before you write code.
