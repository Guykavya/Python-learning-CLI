## Hint 1

Run the first version. Read the last line of the error message carefully: which word does
it use for what `YES` is doing?

## Hint 2

Add `print(YES)` after the `match` in the "fixed" version and type `n`.

## Hint 3

Patterns like `case [x, y]:` must be able to **bind** new names. How could Python tell
`case x:` (bind) from "compare with the existing x"? What does a dot change?
