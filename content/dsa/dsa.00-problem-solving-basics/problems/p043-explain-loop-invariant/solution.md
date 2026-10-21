The model answer is shown when you check. The ideas that must appear:

1. **Euclid invariant:** `gcd(a, b)` stays equal to the gcd of the original pair. Reason: `a % b = a - q * b`, so any
   common divisor of `a` and `b` divides `a % b`, and any common divisor of `b` and `a % b` divides `a`. Same common
   divisors, same gcd.
2. **Euclid stops:** the new `b` is `a % b`, which is less than the old `b` and at least 0. A non-negative whole number
   cannot decrease forever.
3. **Euclid correct:** at the stop `b == 0`, and `gcd(a, 0) = a`, so `a` is the answer.
4. **Largest-so-far invariant:** `largest` is the biggest of the numbers read so far. It stops after `n - 1` passes,
   when all numbers are read, so it holds the maximum.
5. **Starting at 0:** 0 is not an input value, so the invariant is false from the start. With all-negative input
   (like -5, -2, -9) it prints 0 instead of -2.
