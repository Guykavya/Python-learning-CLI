## Hint 1

Python treats a value as false only if it is "empty" or "zero" in some way. Which values are zero or empty?

## Hint 2

For strings, only the empty string `""` is false. The content of a non-empty string does not matter.

## Hint 3

`x or y` returns `x` if `x` is truthy, otherwise `y`. `x and y` returns `x` if `x` is falsy,
otherwise `y`. They return one of the operands, not necessarily a bool.
