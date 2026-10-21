## Hint 1

`//` rounds toward **negative infinity**, not toward zero. Where does -3.5 go on a number line when you round down?

## Hint 2

Python keeps this rule true for every pair: `(a // b) * b + (a % b) == a`. Use it to find each `%` result from the `//` result.

## Hint 3

`int()` is different from `//`: it simply cuts off the decimal part (toward zero).
