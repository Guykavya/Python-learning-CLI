## What a good answer contains

- The exact condition `gcd(a, m) = 1`, with one example for each outcome.
- The reason: a common divisor `d > 1` divides every value `a * x - k * m`, so the remainder 1 cannot appear.
- Fermat: only for a prime modulus; the formula `a^(m-2)` is unreliable otherwise.
- Extended Euclid: `a*x + m*y = gcd`, so `x` is the inverse when `gcd = 1`; works for every modulus and detects failure.
- A sensible choice for each situation.

## Rate yourself

- 3 points: you gave the condition `gcd = 1` with a working example and a failing one.
- 3 points: you explained why a common factor blocks the inverse.
- 2 points: you said Fermat needs a prime modulus and showed a failure.
- 2 points: you explained extended Euclid and the `x % m` step.

8 or more means you are ready for the problems that use both methods.
