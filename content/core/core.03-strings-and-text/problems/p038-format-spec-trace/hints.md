## Hint 1

Read each spec left to right: fill and align, sign, `0`, width, grouping, precision, type. Numbers are right-aligned by default.

## Hint 2

Width counts every character, including the decimal point, commas and the sign. With `^` and an odd amount of padding, the extra space goes on the right.

## Hint 3

For a string, precision cuts. `{n // 10}` inside the spec is 4. The `=` form prints the expression text exactly as written, including spaces, then the formatted value.
