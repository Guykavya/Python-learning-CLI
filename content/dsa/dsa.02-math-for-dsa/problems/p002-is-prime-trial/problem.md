# Is it prime?

A **prime** is an integer greater than 1 whose only divisors are 1 and itself. For each query number, print
`prime` or `composite`. (1 is neither prime nor composite in maths; here print `composite` for 1.)

Use **trial division**: try the divisors 2, 3, 4, ... and stop as soon as `i * i > n`. Write the loop
condition as `i * i <= n`. Do not use `math.sqrt` (floats can be off by one for big numbers).

## Input

- Line 1: `q`.
- The next `q` lines: one integer `n` each.

## Output

`q` lines: `prime` or `composite`.

## Example

Input:

```
5
2
15
97
1
49
```

Output:

```
prime
composite
prime
composite
composite
```

## Constraints

- `1 <= q <= 100`
- `1 <= n <= 10^9`

Trying every `d` up to `n` takes billions of steps for the biggest inputs. Stopping at the square root
needs at most about 31623 steps per query.

Use `input()` without a prompt message.
