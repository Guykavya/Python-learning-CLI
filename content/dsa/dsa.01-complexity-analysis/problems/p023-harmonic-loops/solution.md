## Walkthrough

`count` is `n // 1 + n // 2 + ... + n // n`.

- `n = 1`: 1.
- `n = 6`: 6 + 3 + 2 + 1 + 1 + 1 = 14.
- `n = 12`: 12 + 6 + 4 + 3 + 2 + 2 + 1 + 1 + 1 + 1 + 1 + 1 = 35.
- `n = 30`: 30 + 15 + 10 + 7 + 6 + 5 + 4 + 3 + 3 + 3 (i = 1..10, total 86), then 2 for i = 11..15 (10),
  then 1 for i = 16..30 (15): 86 + 10 + 15 = 111.

Output:

```
1 1
6 14
12 35
30 111
```

## Key idea

1. For a given `i`, the inner loop runs `n // i` times.
2. Each pair `(i, j)` with `i` dividing `j` is counted once, so `count` is also the total number of divisors of all
   numbers from 1 to `n`. (For `n = 6`: 1 + 2 + 2 + 3 + 2 + 4 = 14.)
3. The total is at most `n * (1 + 1/2 + ... + 1/n)`, about `n ln n`. So the double loop is **O(n log n)**, not
   O(n^2). For `n = 10^6` that is about 1.4 * 10^7 steps, a second or two in Python. This pattern is how the sieve
   of Eratosthenes and "for every number, list its multiples" algorithms stay fast. You will use it in dsa.02.
