- Treating 1 as prime, or starting the count so that 2 is missed. Then every answer is shifted by
  one prime.
- Using `d * d < x` instead of `d * d <= x`. Squares of primes (9, 25, 49) then pass as primes,
  because their only small divisor is exactly the square root.
- Dividing by every number below `x`. For `k = 20000` that is billions of divisions and the program
  never finishes in time; the square-root bound needs only a few hundred per candidate.
- Forgetting to reset `is_prime = True` and `d = 3` for each new candidate. One composite number
  then marks all following numbers as composite, or the inner loop never runs again.
