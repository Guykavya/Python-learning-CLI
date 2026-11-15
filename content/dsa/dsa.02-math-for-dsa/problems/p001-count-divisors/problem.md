# Count the divisors

A **divisor** of `n` is a number `d` such that `n % d == 0`. For example, the divisors of 12 are
1, 2, 3, 4, 6 and 12, so 12 has 6 divisors. Note that 1 and `n` itself both count.

You get several numbers. For each one, print how many divisors it has.

Try every `d` from 1 to `n` and count the ones that divide `n`. (A faster way comes in later problems.)

## Input

- Line 1: `q`, the number of queries.
- The next `q` lines: one integer `n` each.

## Output

`q` lines, the number of divisors of each `n`.

## Example

Input:

```
3
12
7
1
```

Output:

```
6
2
1
```

12 has six divisors. 7 is prime: only 1 and 7. 1 has just one divisor, itself.

## Constraints

- `1 <= q <= 10`
- `1 <= n <= 100000`

Use `input()` without a prompt message.
