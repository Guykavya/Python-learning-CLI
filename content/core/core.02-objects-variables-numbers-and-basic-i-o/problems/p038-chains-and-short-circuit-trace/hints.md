## Hint 1

`a < b > c` means `a < b and b > c`. There is no hidden comparison between `a` and `c`.

## Hint 2

`and` stops at the first falsy operand and returns it. `or` stops at the first truthy operand and
returns it. Whatever is after the stopping point is never evaluated, so `1 / 0` may never run.

## Hint 3

`(x := 7)` assigns 7 to `x` **and** gives 7 as the value of the expression.
