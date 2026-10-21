## Hint 1

When a number is exactly halfway between two candidates, `round()` picks the **even** one. Which
of 0 and 1 is even? Of 2 and 3?

## Hint 2

Is `2.675` really stored as 2.675? Is `0.125` (which is 1/8) stored exactly?

## Hint 3

`round(x)` with one argument returns an `int`. `round(x, n)` returns the same type as `x`.
A negative `n` rounds to tens, hundreds and so on. `int()` does not round at all: it truncates toward zero.
