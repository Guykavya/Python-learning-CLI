# Leap year

Read a year and decide whether it is a leap year in the Gregorian calendar (the one used today).

The rule has three parts:

1. A year divisible by 4 is a leap year,
2. **except** a year divisible by 100 is not a leap year,
3. **except** a year divisible by 400 *is* a leap year after all.

So 2024 is a leap year (divisible by 4), 1900 is not (divisible by 100 but not 400), and 2000 is (divisible by 400).

Apply the rule to every year in the given range, even very early or very far-future years.

## Input

One line with an integer `year`.

## Output

One line: `leap` if the year is a leap year, otherwise `not leap` (lowercase, one space between the words).

## Examples

| Input | Output | Why |
|---|---|---|
| `2024` | `leap` | divisible by 4, not by 100 |
| `2023` | `not leap` | not divisible by 4 |
| `1900` | `not leap` | divisible by 100, not by 400 |
| `2000` | `leap` | divisible by 400 |

## Constraints

- `1 <= year <= 10^9`

Use `input()` without a prompt message.

## Before you code

Decide the order of your checks. Try your plan on 1900 and 2000 by hand. Which check must come first so that 2000 is not wrongly rejected?
Write your plan as comments at the top of `solution.py`.
