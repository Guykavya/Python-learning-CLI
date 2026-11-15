## Hint 1

Start with the loop that reads and checks a command and prints `error`; leave the real work for later. What are the four
checks, in what order? (unknown name, argument count, digits only, range.)

## Hint 2

Write the ten functions one at a time. Keep tools you already know from this module: `gcd` by Euclid, `lcm = a // g * b`,
`ext` for `inv`, binary exponentiation for `pow`, `n & (n - 1)` for `popcount`. For `ncr` with any modulus, compute the exact
value with `c = c * (n - i) // (i + 1)` (the division is exact at every step) and take `% m` at the end.

## Hint 3

```
ARGS = {name: number of arguments}
read k
repeat k times:
    parts = input().split()
    if no parts or parts[0] not in ARGS: print error
    elif wrong count: print error
    elif any argument not digits: print error
    else: values = ints; dispatch to the function; print its result
```
Edge cases to test by hand: `lcm 0 0` (no division by zero), `pow 5 0 1` (0, not 1), `inv 5 1` (0), `factor 1` (`1`), `sieve 1` (`none`).
