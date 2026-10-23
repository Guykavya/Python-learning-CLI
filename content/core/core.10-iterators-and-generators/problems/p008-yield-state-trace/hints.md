## Hint 1

Calling `steps()` does not run any of its body. What runs on the first `next(g)`? Where does it stop?

## Hint 2

Mark the position of the generator after each `next`. Between two `next` calls, no generator code runs, so only the lines in the main program print.
