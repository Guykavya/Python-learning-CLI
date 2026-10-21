## Hint 1

Which of the three functions has a `return` with a value? What do the others give back?

## Hint 2

`print(x)` first works out `x`. If `x` is a call to a function that prints, that printing happens **before** the outer `print` shows anything.

## Hint 3

`show(3)` prints `6` and returns `None`. So `print(show(3))` prints two lines: `6` then `None`.
