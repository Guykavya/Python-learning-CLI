## Hint 1

Why does the starter print `1024.0` instead of `1024`? What type does `math.pow` return?

## Hint 2

`2 ** n` with two ints gives an int, and Python ints can hold any number of digits.

## Hint 3

The last three digits are the remainder after dividing by 1000: `p % 1000`.
