## Hint 1

Delete every `assert` line from the function and run the two calls in your head. That is
exactly what `-O` does.

## Hint 2

For each check, ask: "Can this be false if my code is correct and only the user typed something
odd?" If yes, it is input validation.

## Hint 3

Which check is already guaranteed by the checks before it? That one is an invariant.
