# Star triangle

Read a whole number `n` and print a right-angled triangle of stars `*` with `n` rows.

Row 1 has 1 star, row 2 has 2 stars, and so on, up to row `n` with `n` stars.
There are no spaces anywhere: the stars in a row touch each other, and every row starts at the left edge.

## Input

One line with an integer `n`.

## Output

Exactly `n` lines. Line `i` (counting from 1) contains `i` stars and nothing else.
If `n` is 0, print nothing.

## Examples

Input `4`:

```
*
**
***
****
```

Input `1`:

```
*
```

Input `0`: no output at all.

## Constraints

- `0 <= n <= 50`

Use `input()` without a prompt message.

## Before you code

How many stars does row 3 have? Row `i`? Write the rule down, then your plan as comments at the top of `solution.py`.
