The model answer is shown when you check. A good answer contains:

1. A restatement with the exact input (one integer `n`, 1 to 10^6) and exact output (one integer, the count).
2. Hand-worked examples with the right answers: `n = 20` gives **2** (7, 16) and `n = 70` gives **10**
   (7, 16, 25, 34, 43, 52, 61, 70, plus 59 and 68 whose digit sum is 14). "Divisible by 7" is not "equal to 7".
3. A plan someone else could code: loop `x` from 1 to `n`, sum the digits of a copy with `% 10` and `// 10`,
   count when the sum `% 7 == 0`, print once at the end.
4. Edge cases with answers: `n = 1` to `6` give 0, `n = 7` gives 1, and 0 is never counted.
5. A work estimate: about 10^6 numbers times at most 7 digits, so about 7 million inner steps,
   around a second in Python, fast enough. O(n * number of digits).

The point of the exercise: the plan, examples and estimate take ten minutes and catch the "digit sum 14"
mistake before any code exists.
