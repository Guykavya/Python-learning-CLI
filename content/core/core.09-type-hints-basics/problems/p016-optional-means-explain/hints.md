## Hint 1

Say it in one sentence: "a value of type `str`, or `None`". Now, does that sentence say anything about whether you may leave the argument out?

## Hint 2

What is the only thing in Python that lets you call a function without giving an argument? Look for `=` in the three headers.

## Hint 3

mypy complains when a value that may be `None` is used with a method that only `str` has. Which check removes `None` before the method call? And what does `None` have to do with the type `str`?
