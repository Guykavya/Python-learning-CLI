# Star pyramid

Read a whole number `n` and print a pyramid of stars that is `n` rows tall and centred.

Row `i` (counting rows from 1 to `n`, top to bottom) has:

- `n - i` spaces at the start, then
- `2 * i - 1` stars (`*`),
- and **nothing after the last star** (no trailing spaces).

If `n` is 0, print nothing at all.

## Input

One line with the integer `n`.

## Output

`n` lines, the rows of the pyramid, from the top (1 star) to the bottom (`2n - 1` stars).

## Examples

Input `4`:

```
   *
  ***
 *****
*******
```

The first row is 3 spaces then 1 star. The last row is 0 spaces then 7 stars.

Input `1`:

```
*
```

Input `0`: no output.

## Constraints

- `0 <= n <= 40`
- Use `input()` without a prompt message.

## Before you code

Make a small table for `n = 4` with three columns: row `i`, number of spaces, number of stars.
Find the formula for each column, then write your plan as comments at the top of `solution.py`.
Remember that `" " * 3` gives three spaces and `"*" * 5` gives five stars.
