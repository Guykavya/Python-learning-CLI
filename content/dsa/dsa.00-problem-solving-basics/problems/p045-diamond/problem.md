# Star diamond

Read a whole number `n` and print a diamond of stars with `2n - 1` rows.

- The **top half** is a centred pyramid of `n` rows: row `i` (for `i = 1` to `n`) has `n - i` spaces, then `2i - 1` stars.
- The **bottom half** is the same pyramid upside down, **without repeating the widest row**. It has `n - 1` rows,
  going from `2n - 3` stars back down to 1 star.
- No spaces after the last star on any row.

If `n` is 0, print nothing.

## Input

One line with the integer `n`.

## Output

`2n - 1` lines forming the diamond (no lines at all when `n` is 0).

## Examples

Input `3`:

```
  *
 ***
*****
 ***
  *
```

Input `1`:

```
*
```

Input `0`: no output.

## Constraints

- `0 <= n <= 30`
- Use `input()` without a prompt message.

## Before you code

Write a table for `n = 3` with columns row number (1 to 5), spaces, stars. Do the bottom rows follow the same
formula as the top rows if you number them differently? Decide between two loops (one per half) or one loop with
a clever formula, and write your plan as comments at the top of `solution.py`. Check your plan on `n = 1`:
the middle row must appear exactly once.
