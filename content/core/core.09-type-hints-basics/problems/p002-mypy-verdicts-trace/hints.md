## Hint 1

For each line, write down the type of the right-hand side, then the type that is expected on the left (a parameter hint, or a variable hint). Do they fit?

## Hint 2

Lines with no variable hint (`a`, `b`, `e`, `f`) can only fail inside the call. The parameter is `n: int`. Is `"4"` an `int`? Is `2.5`? Is `True`?

## Hint 3

For `c`, `d`, `g`, `h`: compare the declared type of the variable with the type of the value stored in it. `double(4)` is an `int`. Is an `int` a `str`? Is it a `float` (think of the numeric tower)?
