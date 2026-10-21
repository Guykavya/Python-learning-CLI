# Number triangle

Read a whole number `n` and print a triangle of `n` rows. Row number `i` (counting from 1)
contains the numbers `1 2 ... i`, separated by single spaces.

For `n = 4` the output is:

```
1
1 2
1 2 3
1 2 3 4
```

## Input

One line: the number `n`. Use `input()` without a prompt message.

## Output

Exactly `n` lines. Line `i` holds the numbers from 1 to `i` in increasing order, with exactly one space
between neighbouring numbers and no space at the start of the line.
If `n` is 0, print nothing at all.

## Examples

Input `3`:

```
1
1 2
1 2 3
```

Input `1`:

```
1
```

Input `0`: no output.

## Constraints

- `0 <= n <= 30`

## Before you code

For `n = 3`, write down how many numbers each row has and what the last number of each row is.
Then write your plan as comments at the top of `solution.py`. Which loop picks the row, and which loop fills it?
