# Build a number theory toolkit

Put the whole module together in one program: a small **command interpreter**. The first line is `k`, then `k` command
lines. For each command print exactly **one** line of output.

## Commands

All arguments are decimal integers `>= 0`. Names are lower case.

| command | output |
|---|---|
| `gcd a b` | the greatest common divisor (`gcd 0 0` is `0`) |
| `lcm a b` | the least common multiple (`0` if `a` or `b` is `0`) |
| `inv a m` | the modular inverse of `a` modulo `m`, in `0..m-1`, or `none` if it does not exist (`m >= 1`; modulo 1 it is `0`) |
| `ncr n r m` | `C(n, r) % m`; `0` if `r > n`; `m >= 1`, **not** necessarily prime |
| `factor n` | prime factorisation as `p^e` pairs in increasing order, separated by spaces (`360` gives `2^3 3^2 5^1`; `1` gives `1`); `n >= 1` |
| `isprime n` | `yes` or `no` |
| `phi n` | Euler's totient of `n` (`n >= 1`) |
| `pow a b m` | `a^b % m` (`m >= 1`; `0^0` is `1`, and everything modulo 1 is `0`) |
| `popcount n` | the number of 1 bits in `n` |
| `sieve n` | all primes `<= n`, increasing, separated by spaces; `none` if there are none |

## Errors

Print `error` (and keep going) for a command that is: an unknown name (case matters), has the wrong number of arguments, has an
argument that is not made only of digits (letters, decimals, `-5`), is blank, or is outside the allowed range written
above (`m = 0`; `n = 0` for `factor` and `phi`).

## Example

Input:

```
8
gcd 12 18
inv 3 11
ncr 10 3 1000000007
factor 360
isprime 97
pow 2 100 13
sieve 30
hello 1 2
```

Output:

```
6
4
120
2^3 3^2 5^1
yes
3
2 3 5 7 11 13 17 19 23 29
error
```

## Constraints

- `1 <= k <= 1000`
- `gcd`, `lcm`: values up to `10^18`
- `inv`: `a` up to `10^18`, `m` up to `10^18`
- `ncr`: `n <= 5000`, `m <= 10^9`
- `factor`, `isprime`, `phi`: `n <= 10^12`
- `pow`: `a, m <= 10^18`, `b <= 10^18`
- `popcount`: `n < 2^64`
- `sieve`: `n <= 10^6`

Use `input()` without a prompt message.

## Plan before you code

1. One small function per command, named after it. Test each by hand on its examples.
2. Which tool does each command need? `gcd`/`lcm`: Euclid. `inv`: extended Euclid. `pow`: binary exponentiation.
   `isprime`/`factor`/`phi`: trial division to `sqrt(n)`. `sieve`: Eratosthenes. `popcount`: `n & (n - 1)`.
3. How do you check arguments? Split the line; check the name; check the count; check every argument with `.isdigit()`;
   then the range. Do all checks **before** you convert or compute.
4. Which commands fail in a naive version? Try `inv 4 10`, `lcm 0 0`, `pow 5 0 1`, `factor 1`, `isprime 49`, `sieve 29`.
