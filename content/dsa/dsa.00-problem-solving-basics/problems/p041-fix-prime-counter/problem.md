# Fix the prime counter

A classmate wrote a program that reads two numbers `a` and `b` and prints how many **primes** `x` there are with
`a <= x <= b` (both ends included). A prime is a whole number greater than 1 whose only divisors are 1 and itself.

Their program is already in `starter.py`. It runs without crashing, and it even gives the right answer for some inputs.
But it has **four** bugs.

Your job: **find and fix each bug.** Do not rewrite the program from scratch. Keep its structure and change as little as
possible. For each bug:

1. Find a small input where the program prints the wrong answer. Work out the right answer by hand.
2. Dry run the program on that input with a trace table (`x`, `d`, `is_prime`, `count`) to see exactly where it goes wrong.
3. Fix that one thing, and re-run all your small inputs.

Copy `starter.py` to `solution.py` (or edit `solution.py` if it already holds the starter) and fix it there.
Write a short comment above each line you change saying which bug it fixes.

## Input

- Line 1: `a`
- Line 2: `b`

## Output

One line: the number of primes `x` with `a <= x <= b`.

## Examples

| `a` | `b` | Output | Primes counted |
|---|---|---|---|
| `1` | `10` | `4` | 2, 3, 5, 7 |
| `7` | `7` | `1` | 7 |
| `1` | `1` | `0` | none (1 is not prime) |
| `24` | `28` | `0` | none (25 = 5 * 5 is not prime) |


## Constraints

- `1 <= a <= b <= 1000000`
- `b - a <= 100000`
- Must finish in well under 10 seconds for the largest ranges.
- Use `input()` without a prompt message.

## Before you fix anything

Make a list of tiny test inputs: one where the range is a single number, one containing 1, one containing a
square of a prime such as 25 or 49, and one where a non-prime comes before a prime. Predict each answer by hand,
then run the starter on each. Every wrong answer points at a bug.
