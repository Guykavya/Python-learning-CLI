# Amicable pairs

The **proper divisors** of a number are its divisors other than the number itself. For 220 they
are 1, 2, 4, 5, 10, 11, 20, 22, 44, 55 and 110, which add up to 284. The proper divisors of 284 are
1, 2, 4, 71 and 142, which add up to 220.

Two different numbers `a < b` form an **amicable pair** when the sum of the proper divisors of `a`
is `b`, **and** the sum of the proper divisors of `b` is `a`. So (220, 284) is an amicable pair.

A number like 6 (1 + 2 + 3 = 6) is "perfect": its sum points back to itself. That is **not** a pair,
because the two numbers must be different.

Read `n` and print every amicable pair whose larger number `b` is at most `n`.

## Input

One line: the integer `n`. Use `input()` without a prompt message.

## Output

- Each pair on its own line as `a b` (smaller first, one space), in increasing order of `a`.
- If there is no pair, print exactly `none`.

## Examples

Input `284`:

```
220 284
```

Input `283` (284 is too big, so the pair does not count):

```
none
```

Input `1300`:

```
220 284
1184 1210
```

## Constraints

- 1 <= n <= 30000
- Time limit: 10 seconds for `n = 30000` (a good solution takes about a second).

## Before you code

There are two separate jobs: (1) compute the sum of proper divisors of one number quickly, and
(2) use it to find pairs without printing any pair twice and without printing perfect numbers.
Plan each part as comments at the top of `solution.py`, and check part (1) on 220 and 284 first.
