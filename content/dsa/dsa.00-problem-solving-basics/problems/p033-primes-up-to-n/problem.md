# All primes up to n

A **prime** is a whole number greater than 1 whose only divisors are 1 and itself.
2, 3, 5, 7 and 11 are prime. 1 is not prime. 9 is not prime (9 = 3 * 3).

Read a whole number `n` and print every prime from 2 up to `n` (including `n` itself if it is prime),
then print how many there were.

## Input

One line with the integer `n`.

## Output

- Line 1: all primes `<= n` in increasing order, separated by single spaces.
- Line 2: the word `count`, a space, and the number of primes, for example `count 4`.

If `n < 2` there are no primes. Then print **only** the line `count 0` (no empty line before it).

## Examples

Input `10`:

```
2 3 5 7
count 4
```

Input `2`:

```
2
count 1
```

Input `1`:

```
count 0
```

## Constraints

- `0 <= n <= 200000`
- Your program must finish `n = 200000` in well under 10 seconds.
- Use `input()` without a prompt message.

## Before you code

The obvious test "try dividing `x` by every number from 2 to `x - 1`" is correct but far too slow for
`n = 200000` (it does billions of divisions). Think about this: if `x = a * b` with `a <= b`, how big
can `a` be? Write down why you only need to try divisors `d` while `d * d <= x`, then write your plan as
comments at the top of `solution.py`.
