# Goldbach split

Goldbach's conjecture says that every even number greater than 2 is the sum of two primes. It has been checked far past
10^6. For each query `n`, find primes `p <= q` with `p + q = n`, choosing the **smallest** `p`.

## Input

- Line 1: `k`, the number of queries.
- Then `k` lines, each with an even number `n`.

## Output

For each query, one line `p q`.

## Example

Input:

```
3
4
10
26
```

Output:

```
2 2
3 7
3 23
```

For 26: 2 + 24 fails (24 is not prime), 3 + 23 works. 10 = 3 + 7 = 5 + 5, and the smaller first prime wins.

## Constraints

- `1 <= k <= 3000`
- `4 <= n <= 10^6`, `n` even

Use `input()` without a prompt message. All queries share the same limit of 10^6. So some work can be done **once**.
