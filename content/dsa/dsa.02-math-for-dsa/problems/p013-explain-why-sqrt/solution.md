The model answer is shown when you check. The ideas that must appear:

1. If `n = a * b` with `a <= b` and both `> sqrt(n)`, then `a * b > n`: impossible. So the smaller factor is `<= sqrt(n)`.
2. After testing all `i <= sqrt(n)` with no hit, no factor pair can exist: `n` is prime.
3. Example: 91 is found at 7 (13 is the partner, not needed); 97 ends after trying 2..9.
4. `10^12`: about `10^6` steps instead of `10^12`.
5. `<=` is needed for squares of primes (9, 25, 49) where the only divisor in range equals the square root.
6. In the sieve, `k * p` for `k < p` was crossed off by a smaller prime already, so crossing starts at `p * p`.
