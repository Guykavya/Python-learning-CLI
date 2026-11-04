# List the primes with a sieve

Print every prime number from 2 up to `n`, in increasing order, on one line separated by spaces.
If there is no prime (that is, `n < 2`), print an empty line.

Use the **sieve of Eratosthenes**:

1. Make a list `is_prime` of `n + 1` booleans, all `True` (except positions 0 and 1).
2. For each `p` from 2 while `p * p <= n`: if `is_prime[p]` is still `True`, cross off the multiples
   `p*p, p*p + p, p*p + 2p, ...` up to `n`.
3. The numbers still marked `True` are the primes.

Testing every number with trial division is too slow for the biggest input.

## Input

One line: `n`.

## Output

All primes `<= n` on one line, separated by single spaces.

## Example

Input:

```
20
```

Output:

```
2 3 5 7 11 13 17 19
```

## Constraints

- `1 <= n <= 1000000`

Use `input()` without a prompt message.
