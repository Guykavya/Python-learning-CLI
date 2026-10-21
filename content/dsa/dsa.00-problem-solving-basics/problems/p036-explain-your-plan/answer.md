**1. Restatement.** The input is one integer `n`, between 1 and one million. For every whole number `x`
from 1 up to and including `n`, add up the digits of `x`. If that digit sum is a multiple of 7, `x` counts.
The output is a single integer: how many `x` count. Nothing else is printed.

**2. Hand-worked examples.**

- `n = 20`: digit sums go 1, 2, ..., 9 for 1 to 9, then 1 (for 10) up to 9 (for 18), 10 (19), 2 (20).
  Only 7 and 16 have digit sum 7. No number up to 20 has digit sum 14. **Answer: 2.**
- `n = 70`: digit sum 7 gives 7, 16, 25, 34, 43, 52, 61, 70. Digit sum 14 gives 59 and 68 (5 + 9, 6 + 8).
  **Answer: 10.** It is easy to forget 59 and 68 if you only think of "digit sum equals 7".
  Divisible by 7 means 7, 14, 21, 28, ...

**3. Plan.**

```
read n
count = 0
for x from 1 to n (inclusive):
    m = x            # work on a copy, x must not be destroyed
    s = 0
    while m > 0:
        s = s + m % 10     # last digit
        m = m // 10        # drop last digit
    if s % 7 == 0:
        count = count + 1
print count
```

**4. Edge cases.**

| case | answer | why |
|---|---|---|
| `n = 1` | 0 | digit sum 1 |
| `n = 6` | 0 | sums 1 to 6, none divisible by 7 |
| `n = 7` | 1 | first qualifying number |
| `n = 20` | 2 | 7 and 16 |
| `n = 70` | 10 | includes 59 and 68 (sum 14) |
| `n = 100` | 13 | adds 77, 86, 95; 100 has sum 1 |
| `n = 10^6` | 142879 | 1000000 itself has digit sum 1 |

Zero is never included (we start at 1), which matters because 0 has digit sum 0 and 0 is divisible by 7.
Using a copy `m` matters: if you run `x //= 10` on the loop variable inside a `while`, the digit loop
still works but any later use of `x` sees 0.

**5. Amount of work.** There are `n = 10^6` values. Each has at most 7 digits, so the inner loop runs at most
7 times, each with a few operations. That is about 7 million inner steps, maybe 20 to 30 million simple
operations in total. At 10 to 50 million per second, this takes roughly 1 second in Python. That is fast
enough. In O() terms the work is O(n * d), where d is the number of digits, about log10(n).

A faster idea exists (the digit sum of `x + 1` is usually the digit sum of `x` plus 1), but it is not needed here,
and the simple plan is easier to get right.

Key ideas to check: input and output stated exactly; digit sums 7 AND 14 (and 21, 28...) count; answers 2 for n = 20 and 10 for n = 70; plan uses % 10 and // 10 on a copy; edge cases n = 1..6 give 0 and n = 7 gives 1; about 7 million steps, roughly a second, fast enough.
