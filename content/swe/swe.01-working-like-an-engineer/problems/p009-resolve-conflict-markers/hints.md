## Hint 1

Read the file line by line and remember **where you are**: outside a block, in our part, or in their part. What does each kind of line do in each state?

## Hint 2

Use `text.split("\n")` and `"\n".join(...)`: then a final newline (an empty last element) and its absence both survive. Count the lines with `enumerate(..., 1)` for the error messages.

## Hint 3

```text
state 0 (outside): "<<<<<<<" -> state 1, remember its line number; ">>>>>>>" -> error; else copy the line
state 1 (ours):    "=======" -> state 2; "<<<<<<<" or ">>>>>>>" -> error; else collect into ours
state 2 (theirs):  ">>>>>>>" -> output the chosen lines, state 0; "<<<<<<<" or "=======" -> error; else collect into theirs
at the end: state != 0 -> error naming the line where the block began
```
