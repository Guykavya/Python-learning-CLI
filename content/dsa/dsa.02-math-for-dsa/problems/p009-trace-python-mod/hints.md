## Hint 1

Take `-17 // 5`. The real quotient is -3.4. Python's `//` rounds toward minus infinity, not toward zero. Which
integer is that?

## Hint 2

Once you have the floor quotient `q`, get the remainder from `r = a - q * b`. Check the sign rule: with a
positive `b`, `r` is between 0 and `b - 1`; with a negative `b`, `r` is between `b + 1` and 0.

## Hint 3

Careful with the lines that are not plain floor division: `int(-17 / 5)` first makes the float -3.4 and `int`
**truncates** toward zero. `-2 ** 2` is `-(2 ** 2)` because `**` binds tighter than the unary minus.
The last line uses floats and prints a float.
