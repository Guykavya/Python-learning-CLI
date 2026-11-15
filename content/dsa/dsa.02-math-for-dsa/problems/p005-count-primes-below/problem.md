# How many primes up to n?

The prime-counting function `pi(n)` is the number of primes `<= n`. For example `pi(10) = 4` (2, 3, 5, 7).

You get many queries. For each `n`, print `pi(n)`.

The numbers are big, and there are many queries, so one idea is needed: **sieve once** up to the largest `n`,
then answer each query from a table of running counts. Do not sieve again for every query, and do not test
numbers one by one.

## Input

- Line 1: `q`.
- The next `q` lines: one integer `n` each.

## Output

`q` lines: `pi(n)` for each query, in order.

## Example

Input:

```
4
10
1
2
100
```

Output:

```
4
0
1
25
```

## Constraints

- `1 <= q <= 100000`
- `1 <= n <= 5000000`

Use `input()` without a prompt message. For many lines, reading everything at once
(`import sys` and `sys.stdin.read().split()`) is faster than 100000 calls to `input()`.
